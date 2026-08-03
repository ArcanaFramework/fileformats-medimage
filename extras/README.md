# FileFormats-Medimage Extras

[![CI/CD](https://github.com/ArcanaFramework/fileformats-medimage/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/ArcanaFramework/fileformats-medimage/actions/workflows/ci-cd.yml)
[![Codecov](https://codecov.io/gh/ArcanaFramework/fileformats-medimage/branch/main/graph/badge.svg?token=UIS0OGPST7)](https://codecov.io/gh/ArcanaFramework/fileformats-medimage)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/fileformats-medimage-extras.svg)](https://pypi.python.org/pypi/fileformats-medimage-extras/)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat)](https://arcanaframework.github.io/fileformats/)

This is a extras module for the
[fileformats-medimage](https://github.com/ArcanaFramework/fileformats-medimage) package, which provides
additional functionality to format classes (i.e. aside from basic identification and validation), such as
conversion tools, metadata parsers, test data generators, etc...

## Prerequisites

In order to perform conversions between DICOM and neuroimaging formats such as NIfTI you
will need to install the following packages

* [Dcm2niix](https://github.com/rordenlab/dcm2niix)
* [MRtrix3](https://github.com/MRtrix3/MRtrix3)

Please see their installation instructions for the best method for your system
(alternatively the
[Test GitHub action](https://github.com/ArcanaFramework/fileformats-medimage-extras/blob/main/.github/workflows/tests.yml)
contains an example installation for Ubuntu)

## Installation

This extension can be installed for Python 3 using *pip*:

```
$ pip3 install fileformats-medimage-extras
```

## License

This work is licensed under a
[Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/)

[![Creative Commons Attribution 4.0 International License](https://i.creativecommons.org/l/by/4.0/88x31.png)](http://creativecommons.org/licenses/by/4.0/)
