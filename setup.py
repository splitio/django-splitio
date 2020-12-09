#!/usr/bin/env python

from os import path
from setuptools import setup

# install_requires = ['splitio_client>=2.2']

with open(path.join(path.abspath(path.dirname(__file__)), 'django_splitio', 'version.py')) as f:
    exec(f.read())

setup(
    name='django_splitio',
    version=__version__,
    description='Split.io Django Application',
    author='Patricio Echague, Sebastian Arrubia',
    author_email='pato@split.io, sebastian@split.io',
    url='https://github.com/splitio/django-splitio',
    license='Apache License 2.0',
    # install_requires=install_requires,
    extras_require={
        'redis': ['splitio_client[redis]>=2.2'],
        'uwsgi': ['splitio_client[uwsgi]>=2.2']
    },
    setup_requires=['flake8', 'coverage'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ],
    packages=['django_splitio'])
