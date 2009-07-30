#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Python microformats parser"""


try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


classifiers = """\
Development Status :: 3 - Alpha
Environment :: Console
Intended Audience :: Information Technology
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
"""

doc_lines = __doc__.split('\n')


setup(
    name='Microtron',
    version='0.11',
    description='Microformats parser',
    author='Andrew McCollum',
    author_email='amccollum@gmail.com',
    license='MIT',
    url='http://github.com/amccollum/microtron',
    packages=find_packages(exclude=['ez_setup']),
    zip_safe=False,
    install_requires=[
        'lxml',
        'isodate',
        ],
    )
