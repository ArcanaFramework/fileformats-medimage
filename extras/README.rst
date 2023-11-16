FileFormats Medimage Extras
===========================
.. image:: https://github.com/ArcanaFramework/fileformats-medimage/actions/workflows/ci-cd.yml/badge.svg
   :target: https://github.com/ArcanaFramework/fileformats-medimage/actions/workflows/ci-cd.yml
.. image:: https://codecov.io/gh/ArcanaFramework/fileformats-medimage/branch/main/graph/badge.svg?token=UIS0OGPST7
   :target: https://codecov.io/gh/ArcanaFramework/fileformats-medimage
.. image:: https://img.shields.io/pypi/pyversions/fileformats-medimage-extras.svg
   :target: https://pypi.python.org/pypi/fileformats-medimage-extras/
   :alt: Supported Python versions
.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat
    :target: https://arcanaframework.github.io/fileformats/
    :alt: Documentation Status


This is a extras module for the
`fileformats-medimage <https://github.com/ArcanaFramework/fileformats-medimage>`__ package, which provides
additional functionality to format classes (i.e. aside from basic identification and validation), such as
conversion tools, metadata parsers, test data generators, etc...


Prerequisites
-------------

In order to perform conversions between DICOM and neuroimaging formats such as NIfTI you
will need to install the following packages

* `Dcm2niix <https://github.com/rordenlab/dcm2niix>`__
* `MRtrix3 <https://github.com/MRtrix3/MRtrix3>`__

Please see their installation instructions for the best method for your system
(alternatively the
`Test GitHub action <https://github.com/ArcanaFramework/fileformats-medimage-extras/blob/main/.github/workflows/tests.yml>`__
contains an example installation for Ubuntu)


Installation
------------

This extension can be installed for Python 3 using *pip*::

    $ pip3 install fileformats-medimage-extras


License
-------

This work is licensed under a
`Creative Commons Attribution 4.0 International License <http://creativecommons.org/licenses/by/4.0/>`_

.. image:: https://i.creativecommons.org/l/by/4.0/88x31.png
  :target: http://creativecommons.org/licenses/by/4.0/
  :alt: Creative Commons Attribution 4.0 International License
