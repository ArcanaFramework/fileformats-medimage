import numpy as np
from fileformats.core import File, FileSet, mark
from fileformats.core.mixin import WithSeparateHeader
from fileformats.text import Json
from fileformats.archive import Gzip
from .base import MedicalImage
from .diffusion import Fslgrad


# ==================
# Other Data Formats
# ==================


class AnalyzeHeader(File):

    ext = ".hdr"

    @property
    def load(self):
        raise NotImplementedError


class Analyze(WithSeparateHeader, NeuroImage):

    ext = ".img"
    header_type = AnalyzeHeader

    @property
    def data_array(self):
        raise NotImplementedError
