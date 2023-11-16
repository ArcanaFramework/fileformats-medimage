import typing as ty
import logging
from fileformats.generic import FileSet
from fileformats.core import hook

logger = logging.getLogger("fileformats")


# =====================================================================
# Custom loader functions for different image types
# =====================================================================


class MedicalImage(FileSet):

    iana_mime: ty.Optional[str] = None
    INCLUDE_HDR_KEYS = None
    IGNORE_HDR_KEYS = None
    binary = True

    @hook.extra
    def read_array(self):
        """
        Returns the binary data of the image in a numpy array
        """
        raise NotImplementedError

    @hook.extra
    def vox_sizes(self) -> ty.Tuple[float]:
        """The length of the voxels along each dimension"""
        raise NotImplementedError

    @hook.extra
    def dims(self) -> ty.Tuple[int]:
        """The dimensions of the image"""
        raise NotImplementedError
