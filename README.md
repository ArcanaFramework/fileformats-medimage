# FileFormats - Medimage

[![CI/CD](https://github.com/ArcanaFramework/fileformats-medimage/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/ArcanaFramework/fileformats-medimage/actions/workflows/ci-cd.yml)
[![Codecov](https://codecov.io/gh/ArcanaFramework/fileformats-medimage/branch/main/graph/badge.svg?token=UIS0OGPST7)](https://codecov.io/gh/ArcanaFramework/fileformats-medimage)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/fileformats-medimage.svg)](https://pypi.python.org/pypi/fileformats-medimage/)
[![Latest Version](https://img.shields.io/pypi/v/fileformats-medimage.svg)](https://pypi.python.org/pypi/fileformats-medimage/)

This is an extension module to the [fileformats](https://github.com/ArcanaFramework/fileformats) package,
which that adds support for commonly used medical imaging formats, such as DICOM (sets/directories),
NIfTI, and MRtrix Image Format, etc...

## Quick Installation

This extension can be installed for Python 3 using *pip*:

```
$ pip3 install fileformats-medimage
```

This will install the core package and any other dependencies to validate the file formats.

To use converters and metadata reading methods that depend on third-party packages, also install the
associated `extras` package:

```
$ pip3 install fileformats-medimage-extras
```

For most of the converters to work, you will need to install the [Dcm2NiiX](https://github.com/rordenlab/dcm2niix) and [MRtrix](https://mrtrix.readthedocs.io/en/latest/) software packages.
There are various ways to do this, but on Ubuntu you can install [Dcm2NiiX](https://github.com/rordenlab/dcm2niix) with:

```
$ sudo apt install libopenjp2-7
$ curl -fLO https://github.com/rordenlab/dcm2niix/releases/latest/download/dcm2niix_lnx.zip
$ unzip dcm2niix_lnx.zip
$ mv dcm2niix /usr/local/bin
```

(on Mac you can use `Homebrew` instead of `apt` to install libopenjp2-7). [MRtrix](https://mrtrix.readthedocs.io/en/latest/) can
be installed with miniconda:

```
$ conda install -c mrtrix3 mrtrix3
```

## License

This work is licensed under a
[Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/)

## Acknowledgements

The authors acknowledge the facilities and scientific and technical assistance of the
National Imaging Facility, a National Collaborative Research Infrastructure Strategy (NCRIS) capability.

[![Creative Commons Attribution 4.0 International License](https://i.creativecommons.org/l/by/4.0/88x31.png)](http://creativecommons.org/licenses/by/4.0/)
