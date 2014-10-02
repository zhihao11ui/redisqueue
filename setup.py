#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import redisqueue

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.md').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='redisqueue',
    version=redisqueue.__version__,
    description='Simple Redis Queue Library',
    long_description=readme + '\n\n' + history,
    author='Jeff Kehler',
    author_email='jeffrey.kehler@gmail.com',
    url='https://github.com/DevKeh/redisqueue',
    packages=['redisqueue'],
    include_package_data=True,
    install_requires=['redis'],
    license=redisqueue.__license__,
    zip_safe=False,
    keywords='redis queue',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    test_suite='tests',
)
