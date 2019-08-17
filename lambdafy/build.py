import json
import os
import platform

import shutil
import subprocess
import uuid

import boto3

from lambdafy.config import *

from lambdafy.logger import lambdafy_logger as logger


def __clean__():
    shutil.rmtree(WORK_DIR, ignore_errors=True)
    logger.info('build directory {} cleaned'.format(WORK_DIR))


def __copy_src__(path):
    if os.path.isfile(path):
        os.makedirs(PACKAGE_DIR)
        shutil.copy(path, PACKAGE_DIR)
    else:
        shutil.copytree(path, PACKAGE_DIR)
    logger.info('source files copied into package')


def __install__(dependencies_list):
    for dep in dependencies_list:
        subprocess.call(['pip', 'install', '--target', PACKAGE_DIR, dep])
    logger.info('dependencies installed into the package')


def __zip__():
    shutil.make_archive(PACKAGE_NAME, 'zip', PACKAGE_DIR)
    logger.info('package archived into a zip file, check the directory: {}'.format(WORK_DIR))


def local_build(path, dependencies_list):
    # check if local build is running inside docker container
    if os.path.isfile('./.dockerenv'):
        logger.info('starting build inside docker container using python {} installed in the container'
                    .format(platform.python_version()))
    else:
        logger.info('starting local build using python {} installed in the environment'
                    .format(platform.python_version()))

    __clean__()
    __copy_src__(path)
    __install__(dependencies_list)
    __zip__()


def docker_build(path, dependencies_list, python_version):
    logger.info('starting docker build using python {}. This will internally call local build inside '
                'a docker container'.format(python_version))

    cwd = os.getcwd()
    py_env = None
    if python_version == '2':
        py_env = PY_ENV_2
    elif python_version == '3':
        py_env = PY_ENV_3

    build_path_env = path
    dependencies_list_env = ','.join(dependencies_list)

    subprocess.call(['docker', 'run', '--rm', '-v', cwd + ':' + DOCKER_WORKDIR,
                     '-e', 'py_env=' + py_env,
                     '-e', 'build_path=' + build_path_env,
                     '-e', 'dependencies_list=' + dependencies_list_env,
                     DOCKER_IMAGE])


def ec2_build(path, dependencies_list, python_version, aws_access_key, aws_secret_key):
    # create clients
    if aws_secret_key is not None and aws_secret_key is not None:
        logger.info('using aws credentials passed as command line arguments')
        sts_client = boto3.client('sts', aws_access_key_id=aws_access_key,
                                  aws_secret_access_key=aws_secret_key,
                                  region_name=AWS_BUILD_REGION)
        iam_client = boto3.client('iam', aws_access_key_id=aws_access_key,
                                  aws_secret_access_key=aws_secret_key,
                                  region_name=AWS_BUILD_REGION)
        ec2_client = boto3.client('ec2', aws_access_key_id=aws_access_key,
                                  aws_secret_access_key=aws_secret_key,
                                  region_name=AWS_BUILD_REGION)
        s3_client = boto3.client('s3', aws_access_key_id=aws_access_key,
                                 aws_secret_access_key=aws_secret_key,
                                 region_name=AWS_BUILD_REGION)
    else:
        logger.info('using credentials from aws configuration')
        sts_client = boto3.client('sts', region_name=AWS_BUILD_REGION)
        iam_client = boto3.client('iam', region_name=AWS_BUILD_REGION)
        ec2_client = boto3.client('ec2', region_name=AWS_BUILD_REGION)
        s3_client = boto3.client('s3', region_name=AWS_BUILD_REGION)

    account_id = sts_client.get_caller_identity()['Account']

    iam_role_name = AWS_RESOURCE_PREFIX + account_id
    s3_bucket_name = AWS_RESOURCE_PREFIX + account_id

    __check_or_create_role__(iam_client, iam_role_name)
    __check_or_create_bucket__(s3_client, s3_bucket_name)

    __clean__()
    __copy_src__(path)
    __zip__()

    __create_ec2_instance__(ec2_client, iam_role_name)


def __check_or_create_role__(iam_client, iam_role_name):
    role_exists = False
    roles_response = iam_client.list_roles()
    for role in roles_response['Roles']:
        role_name = role['RoleName']

        if role_name == iam_role_name:
            logger.info('IAM role exists, skipping creation')
            role_exists = True
            break

    if role_exists:
        logger.info('IAM role to access S3 exists, skipping creation')
        return

    iam_client.create_instance_profile(InstanceProfileName=iam_role_name)

    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    response = iam_client.create_role(RoleName=iam_role_name,
                                      AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                                      Description='auto generated by lambdafy, used by EC2 and has access to S3')

    role_arn = response['Role']['Arn']
    iam_client.attach_role_policy(RoleName=iam_role_name, PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess')

    iam_client.add_role_to_instance_profile(InstanceProfileName=iam_role_name, RoleName=iam_role_name)

    logger.info('IAM role created {}'.format(role_arn))


def __check_or_create_bucket__(s3_client, bucket_name):
    # create bucket operation is idempotent
    s3_client.create_bucket(Bucket=bucket_name)
    logger.info('asserted that S3 bucket exists')


def __create_ec2_instance__(ec2_client, role_name, bucket_name, python_version, dependencies_list):
    instance_profile = {
        "Name": role_name
    }
    file_dir = os.path.dirname(os.path.abspath(__file__))
    ec2_build_script_file = file_dir + '../ec2/ec2_build.sh'

    with open(ec2_build_script_file, 'r') as f:
        user_data = f.readline()

    py_env = None
    if python_version == '2':
        py_env = PY_ENV_2
    elif python_version == '3':
        py_env = PY_ENV_3

    build_id = str(uuid.uuid4())
    dependencies_list_env = ','.join(dependencies_list)

    user_data.format(py_env=py_env, bucket_name=bucket_name, build_id=build_id, dependencies=dependencies_list_env)

    response = ec2_client.run_instances(ImageId=AMAZON_LINUX_2_AMI,
                                        InstanceType=EC2_DEFAULT_INSTANCE_TYPE,
                                        MaxCount=1, MinCount=1,
                                        IamInstanceProfile=instance_profile,
                                        UserData=user_data)

    instance_id = response['Instances'][0]['InstanceId']
    return instance_id


def __terminate_ec2_instance__(ec2_client, instance_id):
    ec2_client.terminate_instances(InstanceIds=[instance_id])
