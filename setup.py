# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open("README.rst") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="postlookup",
    version="0.1.0",
    description="Set postfix transport based on mx lookups",
    long_description=readme,
    author="Sebastian Dyroff",
    author_email="postlookup@dyroff.org",
    url="https://github.com/sdyroff/postlookup",
    license=license,
    packages=find_packages(exclude=("tests", "docs")),
    entry_points={"console_scripts": ["postlookup = postlookup.postlookup:main"]},
)
