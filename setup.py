#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['pandas>=0.23.4', 'tqdm>=4.28']
test_requirements = ['pytest', ]

setup(
    author='Saket Choudhary',
    author_email='saketkc@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Python package for interacting with SRAdb and downloading datasets from SRA",
    entry_points={
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pysradb',
    name='pysradb',
    packages=['pysradb'],
    setup_requires=requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/saketkc/pysradb',
    version='0.3.0',
    zip_safe=False,
)
