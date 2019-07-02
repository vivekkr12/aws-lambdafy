import boto3
import click

import dateutil.parser as df
from dateutil import tz

from lambdafy.config import *


def deploy_lambda(function_name, aws_access_key, aws_secret_key, aws_region):
    if aws_access_key is not None and aws_secret_key is not None and aws_region is not None:
        click.echo('using credentials and region passed as command line arguments')
        lambda_client = boto3.client('lambda', aws_access_key_id=aws_access_key,
                                     aws_secret_access_key=aws_secret_key,
                                     region_name=aws_region)

    elif (aws_access_key is None or aws_secret_key is None) and aws_region is not None:
        click.echo('using credentials from default config and region passed as command line argument')
        lambda_client = boto3.client('lambda', region_name=aws_region)

    elif aws_access_key is not None and aws_secret_key is not None and aws_region is None:
        click.echo('using credentials passed as command line argument and region from default config')
        lambda_client = boto3.client('lambda', aws_access_key_id=aws_access_key,
                                     aws_secret_access_key=aws_secret_key, )

    else:
        click.echo('using credentials and region from default config')
        lambda_client = boto3.client('lambda')

    with open(PACKAGE_NAME + '.zip', 'rb') as zip_file:
        file_content = zip_file.read()

    click.echo('updating lambda function code...')
    response = lambda_client.update_function_code(FunctionName=function_name, ZipFile=file_content)
    function_name = response['FunctionName']
    last_modified = response['LastModified']
    last_modified_local = __to_local_timezone__(last_modified)
    click.echo('deploy success - {} last modified at {}'.format(function_name, last_modified_local))


def __to_local_timezone__(d):
    ts_utc = df.parse(d)

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    ts_utc = ts_utc.replace(tzinfo=from_zone)
    ts_local = ts_utc.astimezone(to_zone)

    return ts_local
