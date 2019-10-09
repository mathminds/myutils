========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis|
        |
        | |codeclimate|
    * - package
      - | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/2019fa-csci-utils-mathuser0/badge/?style=flat
    :target: https://readthedocs.org/projects/2019fa-csci-utils-mathuser0
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/csci-e-29/2019fa-csci-utils-mathuser0.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/csci-e-29/2019fa-csci-utils-mathuser0

.. |codeclimate| image:: https://codeclimate.com/github/csci-e-29/2019fa-csci-utils-mathuser0/badges/gpa.svg
   :target: https://codeclimate.com/github/csci-e-29/2019fa-csci-utils-mathuser0
   :alt: CodeClimate Quality Status

.. |commits-since| image:: https://img.shields.io/github/commits-since/csci-e-29/2019fa-csci-utils-mathuser0/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/csci-e-29/2019fa-csci-utils-mathuser0/compare/v0.0.0...master



.. end-badges

An example package. Generated with cookiecutter-pylibrary.

Installation
============

::

    pip install csci-utils

You can also install the in-development version with::

    pip install https://github.com/csci-e-29/2019fa-csci-utils-mathuser0/archive/master.zip


Documentation
=============


https://2019fa-csci-utils-mathuser0.readthedocs.io/


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
