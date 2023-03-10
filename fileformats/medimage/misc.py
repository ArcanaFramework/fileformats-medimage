from fileformats.generic import File
from fileformats.core.mixin import WithSeparateHeader
from .base import MedicalImage


# ==================
# Other Data Formats
# ==================


class AnalyzeHeader(File):

    ext = ".hdr"

    @property
    def load(self):
        raise NotImplementedError


class Analyze(WithSeparateHeader, MedicalImage, File):

    ext = ".img"
    header_type = AnalyzeHeader

    @property
    def data_array(self):
        raise NotImplementedError
