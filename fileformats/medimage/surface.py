from fileformats.core import FileSet
from fileformats.application import Xml


class SurfaceMesh(FileSet):
    ...


class Gifti(SurfaceMesh, Xml):

    ext = ".gii"
