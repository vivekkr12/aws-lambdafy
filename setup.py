import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

with open('requirements.txt', 'r') as req:
    requirements = req.readlines()

setuptools.setup(
    name='lambdafy',
    version='0.0.1',
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
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ]
)
