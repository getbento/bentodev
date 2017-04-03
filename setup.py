"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bentodev',
    version='0.0.1',
    description='BentoBox Local Development System',
    long_description=long_description,
    url='https://github.com/getbento/bentodev',
    author='BentoBox',
    author_email='dylan@getbento.com',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='bentobox bentodev',
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        bentodev=bentodev.main:cli
    ''',
)
