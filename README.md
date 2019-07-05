# AWS Lambdafy

Package and Deploy AWS lambda functions in Python

[AWS Lambda](https://aws.amazon.com/lambda/) functions which have dependencies (other than the AWS Python) must be 
packaged SDK must be [packaged into a zip file](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html) 
for deployment. This project aims to streamline that workflow.

AWS Lambdafy is a command line tool built using [Click](https://click.palletsprojects.com/en/7.x/) which packages the 
lambda function with dependencies into a zip file and pushes it to AWS to update the function.

## Quick Start

Install AWS Lambdafy and verify by checking the version. See help for more options
```bash
$ pip install lambdafy
$ lambdafy version
$ lambdafy --help
```

From the root of the project run
```bash
$ lambdafy build --path my_function.py
$ lambdafy deploy
```
