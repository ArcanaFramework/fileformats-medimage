import typing as ty
from fileformats.generic import FileSet
from fileformats.core import mark


# =====================================================================
# Custom loader functions for different image types
# =====================================================================


class MedicalImage(FileSet):

    iana_mime: ty.Optional[str] = None
    INCLUDE_HDR_KEYS = None
    IGNORE_HDR_KEYS = None
    binary = True

    @mark.extra
    def read_array(self):
        """
        Returns the binary data of the image in a numpy array
        """
        raise NotImplementedError

    @mark.extra
    def vox_sizes(self) -> ty.Tuple[float]:
        """The length of the voxels along each dimension"""
        raise NotImplementedError

    @mark.extra
    def dims(self) -> ty.Tuple[int]:
        """The dimensions of the image"""
        raise NotImplementedError
