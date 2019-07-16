import os

import shutil
import subprocess

from lambdafy.config import *


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


def docker_build(path, dependencies_list, python_version):
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
    __install__(dependencies_list)
