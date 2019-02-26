#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The setup script."""

from setuptools import setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["pandas>=0.23.4", "tqdm>=4.28", "click>=7.0"]
test_requirements = ["pytest"]

setup(
    author="Saket Choudhary",
    author_email="saketkc@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    description="Python package for interacting with SRAdb and downloading datasets from SRA",
    entry_points={"console_scripts": ["pysradb=pysradb.cli:cli"]},
    install_requires=requirements,
    license="BSD license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="pysradb",
    name="pysradb",
    packages=["pysradb"],
    python_requires='>=3',
    setup_requires=requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/saketkc/pysradb",
    version="0.8.0",
    zip_safe=False,
)
