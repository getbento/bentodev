from os import path
from codecs import open
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    print("Please install setuptools: pip install setuptools")
    sys.exit(1)

import os.path
sys.path.insert(0, os.path.abspath('lib'))
from bentodev.release import __version__, __author__

here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'requirements.txt'), encoding='utf-8') as requirements_file:
    install_requirements = requirements_file.read().splitlines()
    if not install_requirements:
        print("Unable to read requirements from the requirements.txt file.")
        sys.exit(2)

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bentodev',
    version=__version__,
    description='BentoBox Local Development System',
    long_description=long_description,
    url='https://github.com/getbento/bentodev',
    author=__author__,
    author_email='dylan@getbento.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Build Tools',
    ],
    keywords='bentobox bentodev',
    install_requires=install_requirements,
    package_dir={'': 'lib'},
    packages=find_packages('lib'),
    package_data={
        '': [
            'setup_files/base_config.json',
            'setup_files/config.json',
            'templates/*/*/*',
        ],
    },
    scripts=[
        'bin/bentodev'
    ],
    entry_points='''
        [console_scripts]
    ''',
)
