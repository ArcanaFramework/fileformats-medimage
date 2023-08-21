import typing as ty
from fileformats.core import mark
from fileformats.core.mixin import WithAdjacentFiles
from fileformats.generic import File
from .nifti import NiftiGzX, NiftiGz, Nifti1, NiftiX


class DwiEncoding(File):

    iana_mime: ty.Optional[str] = None

    @mark.extra
    def read_array(self):
        "Both the gradient direction and weighting combined into a single Nx4 array"
        raise NotImplementedError

    @property
    def array(self):
        return self.read_array()

    @property
    def directions(self):
        "gradient direction and weighting combined into a single Nx4 array"
        return self.array[:, :3]

    @property
    def b_values(self):
        "the b-value weighting"
        return self.array[:, 3]


class Bval(File):

    ext = ".bval"

    @mark.extra
    def read_array(self):
        raise NotImplementedError


class Bvec(WithAdjacentFiles, DwiEncoding):
    """FSL-style diffusion encoding, in two separate files"""

    ext = ".bvec"

    @mark.required
    @property
    def b_values_file(self) -> Bval:
        return Bval(self.select_by_ext(Bval))


# NIfTI file format gzipped with BIDS side car
class WithBvec(WithAdjacentFiles):
    @mark.required
    @property
    def encoding(self) -> Bvec:
        return Bvec(self.select_by_ext(Bvec))


class NiftiBvec(WithBvec, Nifti1):
    iana_mime = "application/x-nifti2+bvec"


class NiftiGzBvec(WithBvec, NiftiGz):
    iana_mime = "application/x-nifti2+gzip.bvec"


class NiftiXBvec(WithBvec, NiftiX):
    iana_mime = "application/x-nifti2+json.bvec"


class NiftiGzXBvec(WithBvec, NiftiGzX):
    iana_mime = "application/x-nifti2+gzip.json.bvec"
