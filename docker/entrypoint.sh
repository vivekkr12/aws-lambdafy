#!/usr/bin/env bash
# three environment variables will be provided from docker ENV arg

source $py_env/bin/activate
lambdafy build --path $build_path --dependencies $dependencies_list
