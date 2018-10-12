from setuptools import setup, find_packages

setup(
    name='fcli',
    version='1.0.0',
    author='halprin',
    author_email='me@halprin.io',
    description='Helps spread the AwesomeSauce of the Foundational Components team a bit further',
    long_description='A CLI for the QPP Foundational Components team to use to help them do their day to day job.',
    url='https://github.com/halprin/fcli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    install_requires=[
        'click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        fcli=fc.cli.main:cli
    ''',
)
