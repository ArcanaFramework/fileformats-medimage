FileFormats - Medimage
======================
.. image:: https://github.com/ArcanaFramework/fileformats-medimage/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/ArcanaFramework/fileformats-medimage/actions/workflows/tests.yml
.. image:: https://codecov.io/gh/ArcanaFramework/fileformats-medimage/branch/main/graph/badge.svg?token=UIS0OGPST7
   :target: https://codecov.io/gh/ArcanaFramework/fileformats-medimage
.. image:: https://img.shields.io/pypi/pyversions/fileformats-medimage.svg
   :target: https://pypi.python.org/pypi/fileformats-medimage/
   :alt: Supported Python versions
.. image:: https://img.shields.io/pypi/v/fileformats-medimage.svg
   :target: https://pypi.python.org/pypi/fileformats-medimage/
   :alt: Latest Version

This is an extension module to the `fileformats <https://github.com/ArcanaFramework/fileformats>`__ package
, which that adds support for commonly used medical imaging formats, such as DICOM (sets/directories),
NIfTI, and MRtrix Image Format, etc...

Quick Installation
------------------

This extension can be installed for Python 3 using *pip*::

    $ pip3 install fileformats-medimage

This will install the core package and any other dependencies to validate the file formats.

To use converters and load methods use the ``extended`` install option to install additional
dependencies required for these methods::

    $ pip3 install fileformats-medimage[extended]

For most of the converter to work, you will also need to use the ``[extended]`` install option and
install the Dcm2NiiX_ and MRtrix_ software packages. There are various ways to do this, but on
Ubuntu you can install Dcm2NiiX_ with::

   $ sudo apt install libopenjp2-7
   $ curl -fLO https://github.com/rordenlab/dcm2niix/releases/latest/download/dcm2niix_lnx.zip
   $ unzip dcm2niix_lnx.zip
   $ mv dcm2niix /usr/local/bin

(on Mac you can use `Homebrew` instead of ``apt`` to install libopenjp2-7). MRtrix_ can
be installed with miniconda::

   $ conda install -c mrtrix3 mrtrix3


License
-------

This work is licensed under a
`Creative Commons Attribution 4.0 International License <http://creativecommons.org/licenses/by/4.0/>`__

.. image:: https://i.creativecommons.org/l/by/4.0/88x31.png
  :target: http://creativecommons.org/licenses/by/4.0/
  :alt: Creative Commons Attribution 4.0 International License


.. _Dcm2NiiX: https://github.com/rordenlab/dcm2niix
.. _MRtrix: https://mrtrix.readthedocs.io/en/latest/
