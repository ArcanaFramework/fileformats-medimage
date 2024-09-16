import typing
from fileformats.core import extra, validated_property
from fileformats.core.typing import TypeAlias
from fileformats.core.mixin import WithAdjacentFiles
from fileformats.generic import BinaryFile
from .nifti import NiftiGzX, NiftiGz, Nifti1, NiftiX


if typing.TYPE_CHECKING:
    import numpy.typing  # noqa: F401

EncodingArrayType: TypeAlias = (
    typing.Any
)  # In Py<3.9 this is problematic "numpy.typing.NDArray[numpy.floating[typing.Any]]"


class DwiEncoding:
    @extra
    def read_array(self) -> EncodingArrayType:
        "Both the gradient direction and weighting combined into a single Nx4 array"
        raise NotImplementedError

    def array(self) -> EncodingArrayType:
        return self.read_array()

    def directions(self) -> EncodingArrayType:
        "gradient direction and weighting combined into a single Nx4 array"
        return self.array()[:, :3]

    def b_values(self) -> EncodingArrayType:
        "the b-value weighting"
        return self.array()[:, 3]


class Bval(BinaryFile):

    ext = ".bval"

    @extra
    def read_array(self) -> EncodingArrayType:
        raise NotImplementedError


class Bvec(WithAdjacentFiles, DwiEncoding, BinaryFile):
    """FSL-style diffusion encoding, in two separate files"""

    ext = ".bvec"

    @validated_property
    def b_values_file(self) -> Bval:
        return Bval(self.select_by_ext(Bval))


# NIfTI file format gzipped with BIDS side car
class WithBvec(WithAdjacentFiles):
    @validated_property
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
