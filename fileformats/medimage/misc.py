from fileformats.application import Gzip
from fileformats.generic import File
from fileformats.core import hook
from fileformats.core.mixin import WithSeparateHeader, WithMagicVersion
from .base import MedicalImage


# ==================
# Other Data Formats
# ==================


class AnalyzeHeader(File):

    ext = ".hdr"


class Analyze(WithSeparateHeader, MedicalImage, File):

    ext = ".img"
    header_type = AnalyzeHeader


class Mgh(WithMagicVersion, File):
    """
    FreeSurfer 4-dimensional brain images

    See https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/MghFormat
    """

    ext = ".mgh"
    magic_pattern = rb"(....)"  # First integer is the version string

    @hook.check
    def is_supported_version(self):
        self.version == 1


class MghGz(Gzip[Mgh]):
    """
    FreeSurfer 4-dimensional brain images, gzipped

    See https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/MghFormat
    """

    iana_mime = "application/x-mgh+zip"
    ext = ".mgz"
