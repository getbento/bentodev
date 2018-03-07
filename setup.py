#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
import sys
from codecs import open
from shutil import rmtree

try:
    from setuptools import setup, find_packages
except ImportError:
    print("Please install setuptools: pip install setuptools")
    sys.exit(1)

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'bentodev'
DESCRIPTION = 'BentoBox Local Development System'
URL = 'https://github.com/getbento/bentodev'
EMAIL = 'dylan@getbento.com'
AUTHOR = 'Dylan Stein'

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as requirements_file:
    REQUIRED = requirements_file.read().splitlines()
    if not REQUIRED:
        print("Unable to read requirements from the requirements.txt file.")
        sys.exit(2)

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, 'bentodev', '__version__.py')) as f:
    exec(f.read(), about)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system(
            '{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    entry_points={
        'console_scripts': ['bentodev=bentodev.cli:main'],
    },
    install_requires=REQUIRED,
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Build Tools',
    ],
    keywords='bentobox bentodev',
    package_data={
        '': [
            'setup_files/base_config.json',
            'setup_files/config.json',
            'templates/*/*/*',
        ],
    },
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
