import os
import platform

import click

import lambdafy
import lambdafy.build as lb
import lambdafy.deploy as ld


@click.group()
def cli():
    pass


@click.command()
def version():
    python_version = platform.python_version()
    os_name = os.name
    platform_name = platform.system()
    release_version = platform.release()
    arch = platform.architecture()
    click.echo('lambdafy {}\n'
               'Python {}\n'
               '{} {} {} {}'
               .format(lambdafy.__version__, python_version, os_name, platform_name, arch[0], release_version))


@click.command()
@click.option('--env', '-e', default='local', help='location where the project will be build',
              type=click.Choice(['local', 'docker', 'ec2']), show_default=True)
@click.option('--python-version', '-v', default='3', help='python version if using docker or ec2 build',
              type=click.Choice(['2', '3']))
@click.option('--path', '-p', prompt='File name or top level directory name',
              help='file or directory to package')
@click.option('--requirements-file', '-r', default='requirements.txt', help='pip compatible requirements file',
              show_default=True)
@click.option('--dependencies', '-d', default=None, help='comma separated list of dependencies')
def build(env, path, requirements_file, dependencies):
    python_version = platform.python_version()
    click.echo('using python version {} for building.\n'
               'local build uses the runtime configured in the environment.\n'
               'docker and ec2 build defaults to python 3\n'
               'use the --python-version parameter to specify another version if required'
               .format(python_version))

    dependencies_list = []
    if dependencies is not None:
        dependencies_list = dependencies.split(',')
    else:
        if not os.path.isfile(requirements_file):
            click.secho('neither a requirements file was provided nor dependencies were provided as argument.\n'
                        'no dependencies will be packaged.\n'
                        'you can ignore this warning if your project has no dependencies', fg='red')
        else:
            with open(requirements_file, 'r') as req:
                dependencies_list = req.readlines()

    if env == 'local':
        lb.local_build(path, dependencies_list)
    elif env == 'docker':
        lb.docker_build(path, dependencies_list)
    elif env == 'ec2':
        lb.ec2_build(path, dependencies_list)


@click.command()
@click.option('--function-name', '-f', prompt='Lambda Function Name', help='lambda function name')
@click.option('--aws-access-key', '-k', default=None, help='AWS Access Key')
@click.option('--aws-secret-key', '-s', default=None, help='AWS Secret Key')
@click.option('--aws-region', '-r', default=None, help='AWS Region')
def deploy(function_name, aws_access_key, aws_secret_key, aws_region):
    try:
        ld.deploy_lambda(function_name, aws_access_key, aws_secret_key, aws_region)
    except ValueError as ex:
        click.secho(str(ex), fg='red')


cli.add_command(version)
cli.add_command(build)
cli.add_command(deploy)
