#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The setup script."""

from setuptools import setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

with open("requirements.txt") as req_file:
    requirements = [req.strip() for req in req_file.readlines()]

test_requirements = ["pytest"]

setup(
    author="Saket Choudhary",
    author_email="saketkc@gmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    description="A Python package for interacting with SRAdb and downloading datasets from SRA/ENA/GEO",
    entry_points={"console_scripts": ["pysradb=pysradb.cli:parse_args"]},
    install_requires=requirements,
    license="BSD license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="pysradb",
    name="pysradb",
    packages=["pysradb"],
    python_requires=">=3.7",
    setup_requires=requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/saketkc/pysradb",
    version="1.1.0",
    zip_safe=False,
)
