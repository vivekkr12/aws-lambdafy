import boto3

import dateutil.parser as df
from boto3.s3.transfer import S3Transfer
from dateutil import tz

from lambdafy.config import *

from lambdafy.logger import lambdafy_logger as logger


def deploy_lambda(function_name, aws_access_key, aws_secret_key, aws_region, s3_bucket):
    if aws_access_key is not None and aws_secret_key is not None and aws_region is not None:
        logger.info('using credentials and region passed as command line arguments')
        lambda_client = boto3.client('lambda', aws_access_key_id=aws_access_key,
                                     aws_secret_access_key=aws_secret_key,
                                     region_name=aws_region)
        s3_client = boto3.client('s3', aws_access_key_id=aws_access_key,
                                 aws_secret_access_key=aws_secret_key,
                                 region_name=aws_region)

    elif (aws_access_key is None or aws_secret_key is None) and aws_region is not None:
        logger.info('using credentials from default config and region passed as command line argument')
        lambda_client = boto3.client('lambda', region_name=aws_region)
        s3_client = boto3.client('s3', region_name=aws_region)

    elif aws_access_key is not None and aws_secret_key is not None and aws_region is None:
        logger.info('using credentials passed as command line argument and region from default config')
        lambda_client = boto3.client('lambda', aws_access_key_id=aws_access_key,
                                     aws_secret_access_key=aws_secret_key)
        s3_client = boto3.client('s3', aws_access_key_id=aws_access_key,
                                 aws_secret_access_key=aws_secret_key)

    else:
        logger.info('using credentials and region from default config')
        lambda_client = boto3.client('lambda')
        s3_client = boto3.client('s3')

    if s3_bucket is None:
        with open(PACKAGE_NAME + '.zip', 'rb') as zip_file:
            file_content = zip_file.read()

        logger.info('updating lambda function code by direct upload...')
        response = lambda_client.update_function_code(FunctionName=function_name, ZipFile=file_content)
    else:
        s3_key = PACKAGE_NAME + '.zip'
        logger.info('uploading file to s3 bucket {}', s3_bucket)
        s3_transfer = S3Transfer(s3_client)
        s3_transfer.upload_file(PACKAGE_NAME + '.zip', s3_bucket, PACKAGE_NAME + '.zip')

        logger.info('package uploaded to S3, updating lambda function...')
        response = lambda_client.update_function_code(FunctionName=function_name, S3Bucket=s3_bucket, S3Key=s3_key)

    function_name = response['FunctionName']
    last_modified = response['LastModified']
    last_modified_local = _to_local_timezone(last_modified)
    logger.info('deploy success - {} last modified at {}'.format(function_name, last_modified_local))


def _to_local_timezone(d):
    ts_utc = df.parse(d)

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    ts_utc = ts_utc.replace(tzinfo=from_zone)
    ts_local = ts_utc.astimezone(to_zone)

    return ts_local
