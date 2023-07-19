from fileformats.generic import File
from fileformats.core.mixin import WithSeparateHeader
from .base import MedicalImage


# ==================
# Other Data Formats
# ==================


class AnalyzeHeader(File):

    ext = ".hdr"


class Analyze(WithSeparateHeader, MedicalImage, File):

    ext = ".img"
    header_type = AnalyzeHeader
