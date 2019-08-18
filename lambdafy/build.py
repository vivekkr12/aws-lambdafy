import os

import shutil
import subprocess

import boto3

WORK_DIR = '.lambdafy'
PACKAGE_DIR = WORK_DIR + '/package'
PACKAGE_NAME = WORK_DIR + '/lambda_package'
KEY_PAIR_NAME = 'lambdafy'
AMAZON_LINUX_AMI = 'ami-0b898040803850657'


def __clean__():
    shutil.rmtree(WORK_DIR, ignore_errors=True)


def __copy_src__(path):
    if os.path.isfile(path):
        os.makedirs(PACKAGE_DIR, exist_ok=True)
        shutil.copy(path, PACKAGE_DIR)
    else:
        shutil.copytree(path, PACKAGE_DIR)


def __install__(dependencies_list):
    for dep in dependencies_list:
        subprocess.call(['pip', 'install', '--target', PACKAGE_DIR, dep])


def __zip__():
    shutil.make_archive(PACKAGE_NAME, 'zip', PACKAGE_DIR)


def local_build(path, dependencies_list):
    __clean__()
    __copy_src__(path)
    __install__(dependencies_list)
    __zip__()


def docker_build(path, dependencies_list):
    __install__(dependencies_list)


def __execute_commands_on_linux_instances__(client, commands, instance_ids):
    """Runs commands on remote linux instances
    :param client: a boto3 ssm client
    :param commands: a list of strings, each one a command to execute on the instances
    :param instance_ids: a list of instance_id strings, of the instances on which to execute the command
    :return: the response from the send_command function (check the boto3 docs for ssm client.send_command() )
    """

    resp = client.send_command(
        DocumentName="AWS-RunShellScript",  # One of AWS' preconfigured documents
        Parameters={'commands': commands},
        InstanceIds=instance_ids,
    )
    return resp


def ec2_build(path, dependencies_list):
    # zip sources to be transferred
    __clean__()
    __copy_src__(path)
    __zip__()

    # check and crate key pair if not exists
    ec2_client = boto3.resource('ec2', region_name='us-east-1')

    key_pair_response = ec2_client.describe_key_pairs()
    key_pairs = key_pair_response['KeyPairs']

    key_pair_exists = False

    for kp in key_pairs:
        if kp['KeyName'] == KEY_PAIR_NAME:
            key_pair_exists = True
            break

    if not key_pair_exists:
        ec2_client.create_key_pair(KeyName=KEY_PAIR_NAME)

    # Create EC2 instance
    instance_id_list = ec2_client.create_instances(ImageId=AMAZON_LINUX_AMI,
                                                   InstanceType='t3.micro',
                                                   MinCount=1,
                                                   MaxCount=1)
    instance_id = instance_id_list[0].id

    ssm_client = boto3.client('ssm', region_name='us-east-1')
    response = ssm_client.send_command(
        DocumentName='AWS-RunShellScript',  # One of AWS' preconfigured documents
        Parameters={'commands': [
            '',
            '',

        ]},
        InstanceIds=[instance_id],
    )
