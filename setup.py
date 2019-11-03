#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

from ast import literal_eval
import os
DOCKER_DEV = literal_eval(os.environ.get("DEV_CSCI_UTILS", "0"))

def read(*names, **kwargs):
    try:
        with io.open(
            join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
        ) as fh:
            return fh.read()
    except FileNotFoundError:
        if DOCKER_DEV:
            return ""
        raise


extras = {'luigi' : ['luigi>=2.8.9']}
extras['all'] = [item for sublist in extras.values() for item in sublist]


setup(
    name="csci-utils",
    use_scm_version={
        "local_scheme": "node-and-timestamp",
        "write_to": "src/csci_utils/_version.py",
        "fallback_version": "0.0.0",
    } if not DOCKER_DEV else False,
    description="CSCI Utils Package",
    long_description="%s\n%s"
    % (
        re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub(
            "", read("README.rst")
        ),
        re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
    ),
    author="Christopher Lee",
    author_email="chl2967@g.harvard.edu",
    url="https://github.com/csci-e-29/2019fa-csci-utils-mathuser0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        # # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        "Topic :: Utilities",
        "Private :: Do Not Upload",
    ],
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires=">=3.6",
    install_requires=[
        # eg: 'aspectlib==1.1.1', 'six>=1.7',
        "atomicwrites>=1.3.0",
        "numpy>=1.1.0",
        "pandas",
        "xlrd",
        "pyarrow",
        "openpyxl",
        "setuptools_scm",
        "luigi",
    ],
    # extras_require=extras,
    setup_requires=[
        'setuptools_scm>=3.3.1',
    ],
    entry_points={"console_scripts": ["csci-utils = csci_utils.cli:main"]},
)
