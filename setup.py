#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import md5dir

setup(
    name="md5dir",
    version=md5dir.__version__,
    packages=find_packages(),
    author="MachinBrol",
    author_email="zazor@riseup.net",
    description="Compute the md5 sum of a directory",
    long_description=open('README.md').read(),
    licence="WTFPL",
    include_package_data=True,
    url='http://github.com/machinbrol/md5dir',
    install_requires=["click"],
    classifiers=[
        "Programming Language :: Python",
        "Natural Language :: French",
    ],
    entry_points = {
        'console_scripts': [
            'md5dir = md5dir.md5dir:cli',
        ],
    },
)
