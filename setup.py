#!/usr/bin/env python

from os import path
from setuptools import setup
from sys import version_info

tests_require = ['Django>=1.8']
install_requires = ['splitio_client>=2.1', 'redis>=2.10.5', 'jsonpickle>=0.9.3']

if version_info < (3,):
    tests_require += ['mock']

with open(path.join(path.abspath(path.dirname(__file__)), 'django_splitio', 'version.py')) as f:
    exec (f.read())

setup(name='django_splitio',
      version=__version__,
      description='Split.io Django Application',
      author='Patricio Echague',
      author_email='pato@split.io',
      url='https://github.com/splitio/django-splitio',
      license='Apache License 2.0',
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      setup_requires=['flake8', 'coverage'],
      test_suite='django_splitio.runtests.runtests',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries'
      ],
      packages=['django_splitio','django_splitio.templatetags'])
