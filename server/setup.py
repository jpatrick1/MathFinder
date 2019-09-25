#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
from setuptools import setup, find_packages

entrypoint = 'mathfinder'
pkg_name = entrypoint
description = 'HTTP Interface for MathFinder'

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


long_description = read('README.md')

setup(
    name=pkg_name,
    install_requires=[
        'tornado',
        'connexion',
        'swagger-ui-bundle',
        'Pillow'
    ],
    entry_points={
        'console_scripts': [
            '{} = {}.server:main'.format(entrypoint, pkg_name)
        ],
    },
    package_data={
        pkg_name: ['openapi/*.yaml'],
    },
    packages=find_packages(),
    url='',
    license="TBD",
    description=description,
    long_description=long_description,
    zip_safe=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
    ],
)
