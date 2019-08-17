#!/bin/bash

# install dependencies
sudo yum -y update
sudo yum -y install python3
sudo yum -y install git
sudo pip3 install virtualenv

# create virtual environments
virtualenv --python=python pyenvironments/pyenv2
virtualenv --python=python3 pyenvironments/pyenv3

# install lambdafy
source pyenvironments/{py_env}/bin/activate
pip install git+https://github.com/vivekkr12/aws-lambdafy.git@master
lambdafy version

mkdir work
cd work

aws s3 cp s3://{bucket_name}/{build_id}/lambda_package.zip lambda_package.zip
unzip lambda_package.zip package
rm lambda_package.zip

lambdafy --env local --path package --dependencies {dependencies}
aws s3 cp .lambdafy/lambda_package.zip s3://{bucket_name}/{build_id}/lambda_package.zip
