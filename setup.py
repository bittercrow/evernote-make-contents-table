# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name="empj.makecontents",
    version='0.1.0',
    description='Make a table of contents in Evernote\'s notes',
    long_description=readme,
    author='Teruki',
    author_email='ts2003j@gmail.com',
    url='https://localhost:8080',
    license=license,
    packages=['empj.makecontents'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
    ],
)
