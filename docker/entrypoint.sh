#!/usr/bin/env bash
# three environment variables will be provided from docker ENV arg

source /root/.bashrc
conda create -y --name labdafy python=$python_version
conda activate lambdafy

pip install git+https://github.com/vivekkr12/aws-lambdafy.git@master && lambdafy version
lambdafy build --path $build_path --dependencies $dependencies_list
