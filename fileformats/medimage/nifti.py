import typing as ty
from fileformats.generic import File
from fileformats.core.mixin import WithSideCars, WithMagicNumber, WithAdjacentFiles
from fileformats.application import Json
from fileformats.application.archive import BaseGzip
from .base import MedicalImage


class Nifti(MedicalImage, File):

    ext: str = ".nii"
    iana_mime: ty.Optional[str] = None


class WithBids(WithSideCars):

    primary_type = Nifti
    side_car_types = (Json,)

    @property
    def json_file(self) -> Json:
        return Json(self.select_by_ext(Json))  # type: ignore[attr-defined]


class Nifti1(WithMagicNumber, Nifti):

    iana_mime = "application/x-nifti1"
    magic_number = "6E2B3100"
    magic_number_offset = 344


class Nifti2(WithMagicNumber, Nifti):

    iana_mime = "application/x-nifti2"
    magic_number = "6e2b3200"
    magic_number_offset = 344


class NiftiGz(Nifti, BaseGzip):
    ext = ".nii.gz"
    iana_mime = "application/x-nifti1+gzip"
    archived_type = Nifti


class NiftiX(WithBids, Nifti):
    iana_mime = "application/x-nifti1+json"


class NiftiGzX(WithBids, NiftiGz):
    iana_mime = "application/x-nifti1+gzip.bids"


class NiftiDataFile(MedicalImage):

    ext = ".img"


class NiftiWithDataFile(WithAdjacentFiles, Nifti1):
    """Nifti file with separate data file"""

    magic_number = "6E693100"
    alternate_exts = (".hdr",)

    @property
    def data_file(self) -> NiftiDataFile:
        return NiftiDataFile(self.select_by_ext(NiftiDataFile))
