from fileformats.generic import File
from fileformats.core import mark
from fileformats.core.mixin import (
    WithSideCars, WithMagicNumber, WithSeparateHeader, WithAdjacentFiles)
from fileformats.serialization import Json
# from fileformats.text import Tsv
from fileformats.archive import Gzip
from .base import NeuroImage


class Nifti(NeuroImage):

    ext = ".nii"

    def load_metadata(self):
        import nibabel
        return dict(nibabel.load(self.fspath).header)

    @property
    def data_array(self):
        import nibabel
        return nibabel.load(self.fspath).get_data()

    @property
    def vox_sizes(self):
        # FIXME: This won't work for 4-D files
        return self.metadata["pixdim"][1:4]

    @property
    def dims(self):
        # FIXME: This won't work for 4-D files
        return self.metadata["dim"][1:4]


class WithBids(WithSideCars):

    primary_type = Nifti
    side_car_types = (Json,)

    @mark.required
    @property
    def json_file(self):
        return Json(self.select_by_ext(Json))

    # @mark.required
    # @property
    # def tsv_file(self):
    #     return Json(self.select_by_ext(Json, allow_none=True))


class Nifti1(WithMagicNumber, Nifti):

    iana_mime = "application/x-nifti1"
    magic_number = "6E2B3100"
    magic_number_offset = 344


class Nifti2(WithMagicNumber, Nifti):

    ext = ".nii"
    iana_mime = "application/x-nifti2"
    magic_number = "6e2b3200"
    magic_number_offset = 344


class NiftiGz(Nifti, Gzip):  # Should be Gzip[Nifti1]

    ext = ".nii.gz"
    iana_mime = "application/x-nifti1+gzip"


class NiftiX(WithBids, Nifti):
    iana_mime = "application/x-nifti1+json"


class NiftiGzX(WithBids, NiftiGz):
    iana_mime = "application/x-nifti1+gzip.bids"


class NiftiDataFile(NeuroImage):

    ext = ".img"


class NiftiWithDataFile(WithAdjacentFiles, Nifti1):

    magic_number = "6E693100"
    alternate_exts = (".hdr",)

    @mark.required
    @property
    def data_file(self):
        return self.select_by_ext(NiftiDataFile)


class AnalyzeHeader(File):

    ext = ".hdr"
    binary = True

    @property
    def load(self):
        raise NotImplementedError


class Analyze(WithSeparateHeader, NeuroImage):

    ext = ".img"
    header_type = AnalyzeHeader

    @property
    def data_array(self):
        raise NotImplementedError
