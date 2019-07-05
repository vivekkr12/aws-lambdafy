import setuptools

import lambdafy

with open('README.md', 'r') as readme:
    long_description = readme.read()

with open('requirements.txt', 'r') as req:
    requirements = req.readlines()


PACKAGE_NAME = 'lambdafy'
VERSION = lambdafy.__version__


setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author='Vivek Kumar',
    author_email='vivekuma@uw.edu',
    description='Create Python AWS lambda deployment package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/vivekkr12/aws-lambdafy',
    packages=setuptools.find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        lambdafy=lambdafy.main:cli
    ''',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ]
)
