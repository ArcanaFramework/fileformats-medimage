import typing as ty
from fileformats.core import FileSet
from fileformats.application import Xml


class SurfaceMesh(FileSet):

    iana_mime: ty.Optional[str] = None


class Gifti(SurfaceMesh, Xml):

    ext = ".gii"
