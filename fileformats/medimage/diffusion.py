import typing as ty
from fileformats.core import extra
from fileformats.core.mixin import WithAdjacentFiles
from fileformats.generic import File
from .nifti import NiftiGzX, NiftiGz, Nifti1, NiftiX


if ty.TYPE_CHECKING:
    import numpy as np
    import numpy.typing


class DwiEncoding(File):

    iana_mime: ty.Optional[str] = None

    @extra
    def read_array(self) -> "numpy.typing.NDArray[np.floating[ty.Any]]":
        "Both the gradient direction and weighting combined into a single Nx4 array"
        raise NotImplementedError

    def array(self) -> "numpy.typing.NDArray[np.floating[ty.Any]]":
        return self.read_array()

    def directions(self) -> "numpy.typing.NDArray[np.floating[ty.Any]]":
        "gradient direction and weighting combined into a single Nx4 array"
        return self.array()[:, :3]

    def b_values(self) -> "numpy.typing.NDArray[np.floating[ty.Any]]":
        "the b-value weighting"
        return self.array()[:, 3]


class Bval(File):

    ext = ".bval"

    @extra
    def read_array(self) -> "numpy.typing.NDArray[np.floating[ty.Any]]":
        raise NotImplementedError


class Bvec(WithAdjacentFiles, DwiEncoding):
    """FSL-style diffusion encoding, in two separate files"""

    ext = ".bvec"

    @property
    def b_values_file(self) -> Bval:
        return Bval(self.select_by_ext(Bval))


# NIfTI file format gzipped with BIDS side car
class WithBvec(WithAdjacentFiles):
    @property
    def encoding(self) -> Bvec:
        return Bvec(self.select_by_ext(Bvec))  # type: ignore[attr-defined]


class NiftiBvec(WithBvec, Nifti1):
    iana_mime = "application/x-nifti2+bvec"


class NiftiGzBvec(WithBvec, NiftiGz):
    iana_mime = "application/x-nifti2+gzip.bvec"


class NiftiXBvec(WithBvec, NiftiX):
    iana_mime = "application/x-nifti2+json.bvec"


class NiftiGzXBvec(WithBvec, NiftiGzX):
    iana_mime = "application/x-nifti2+gzip.json.bvec"
