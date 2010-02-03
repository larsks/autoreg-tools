import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='autoreg-tools',
        version='20100201.1',
        install_requires=[
            'lxml',
            'configdict',
            'iptools',
            ],
        description='Tools for interacting with FAS Autoreg network registration system.',
        long_description=read('README.rst'),
        author='Lars Kellogg-Stedman',
        author_email='lars@seas.harvard.edu',
        packages=['autoreg'],
        )

