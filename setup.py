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
            join(dirname(__file__), *names),
            encoding=kwargs.get('encoding', 'utf8')
        ) as fh:
            return fh.read()
    except FileNotFoundError:
        if DOCKER_DEV:
            return ""
        raise

setup(
    name='csci-utils',
    use_scm_version={'local_scheme': 'dirty-tag','root': '.', 'relative_to': __file__, 'write_to': 'src/csci_utils/_version.py',
                     "fallback_version": "0.0.0"} if not DOCKER_DEV else False,
    description='CSCI Utils Library',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='AUTHOR',
    author_email='USERNAME@gmail.com',
    url='https://github.com/csci-e-29/2019fa-csci-utils-USERNAME',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
        'Private :: Do Not Upload',
    ],
    project_urls={
        'Changelog': 'https://github.com/csci-e-29/2019fa-csci-utils-USERNAME/blob/master/CHANGELOG.rst',
        'Issue Tracker': 'https://github.com/csci-e-29/2019fa-csci-utils-USERNAME/issues',
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires='>=3.6',
    install_requires=[
        'atomicwrites',
        'pandas',
        'xlrd',
        'pyarrow',
        'xlwt'
    ],
    extras_require={
        'workflow': ['luigi','boto3','moto','dask[dataframe]','toolz'],
    },
    setup_requires=[
        'setuptools_scm>=3.3.1'
    ],
    entry_points={
        'console_scripts': [
            'csci-utils = csci_utils.cli:main',
        ]
    },
)
