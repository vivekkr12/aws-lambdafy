import os
import platform

import shutil
import subprocess

from lambdafy.config import *

from lambdafy.logger import lambdafy_logger as logger


def _clean():
    shutil.rmtree(WORK_DIR, ignore_errors=True)
    logger.info('build directory {} cleaned'.format(WORK_DIR))


def _copy_src(path):
    if os.path.isfile(path):
        os.makedirs(PACKAGE_DIR)
        shutil.copy(path, PACKAGE_DIR)
    else:
        shutil.copytree(path, PACKAGE_DIR)
    logger.info('source files copied into package')


def _install(dependencies_list):
    for dep in dependencies_list:
        subprocess.call(['pip', 'install', '--target', PACKAGE_DIR, dep])
    logger.info('dependencies installed into the package')


def _zip():
    shutil.make_archive(PACKAGE_NAME, 'zip', PACKAGE_DIR)
    logger.info('package archived into a zip file, check the directory: {}'.format(PACKAGE_DIR))


def local_build(path, dependencies_list):
    # check if local build is running inside docker container
    if os.path.isfile('./.dockerenv'):
        logger.info('starting build inside docker container using python {} installed in the container'
                    .format(platform.python_version()))
    else:
        logger.info('starting local build using python {} installed in the environment'
                    .format(platform.python_version()))

    _clean()
    _copy_src(path)
    _install(dependencies_list)
    _zip()


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


def ec2_build(path, dependencies_list, python_version):
    _install(dependencies_list)
