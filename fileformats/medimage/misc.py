from fileformats.application import Gzip
from fileformats.generic import BinaryFile
from fileformats.core import validated_property
from fileformats.core.mixin import WithSeparateHeader, WithMagicVersion
from .base import MedicalImage
from fileformats.core.exceptions import FormatMismatchError


# ==================
# Other Data Formats
# ==================


class AnalyzeHeader(BinaryFile):

    ext = ".hdr"


class Analyze(WithSeparateHeader, MedicalImage, BinaryFile):

    ext = ".img"
    header_type = AnalyzeHeader


class Mgh(WithMagicVersion, BinaryFile):
    """
    FreeSurfer 4-dimensional brain images

    See https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/MghFormat
    """

    ext = ".mgh"
    magic_pattern = rb"(....)"  # First integer is the version string

    @validated_property
    def _is_supported_version(self) -> None:
        assert isinstance(self.version, str)
        if int(self.version) != 1:
            raise FormatMismatchError(
                f"Unsupported version {self.version} found in MGH format {self}"
            )


class MghGz(Gzip[Mgh]):  # type: ignore[type-arg]
    """
    FreeSurfer 4-dimensional brain images, gzipped

    See https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/MghFormat
    """

    iana_mime = "application/x-mgh+zip"
    ext = ".mgz"
