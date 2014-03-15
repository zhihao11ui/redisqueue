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
#history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='redisqueue',
    version=redisqueue.__version__,
    description='Simple Redis Queue Library',
    #long_description=readme + '\n\n' + history,
    author='Jeff Kehler',
    author_email='jeffrey.kehler@gmail.com',
    url='https://github.com/DevKeh/redisqueue',
    packages=[
        'redisqueue',
    ],
    package_dir={'redisqueue': 'redisqueue'},
    include_package_data=True,
    install_requires=['redis'
    ],
    license="MIT",
    zip_safe=False,
    keywords='redis queue',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
    ],
    #test_suite='tests',
)
