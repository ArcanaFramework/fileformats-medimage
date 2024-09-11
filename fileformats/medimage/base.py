import sys
import typing as ty
import logging
from fileformats.core import extra, FileSet, mtime_cached_property
from fileformats.core.mixin import WithClassifiers
from .contents import ContentsClassifier
from .contents.imaging.modality import ImagingModality
from .contents.imaging.derivatives import Derivative
from .contents.anatomical_entity import AnatomicalEntity

logger = logging.getLogger("fileformats")

if sys.version_info >= (3, 9):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

if ty.TYPE_CHECKING:
    import numpy as np
    import numpy.typing


# =====================================================================
# Custom loader functions for different image types
# =====================================================================

DataArrayType: TypeAlias = (
    "numpy.typing.NDArray[ty.Union[np.floating[ty.Any], np.integer[ty.Any]]]"
)


class MedicalImage(WithClassifiers, FileSet):

    iana_mime: ty.Optional[str] = None
    INCLUDE_HDR_KEYS: ty.Optional[ty.Tuple[str, ...]] = None
    IGNORE_HDR_KEYS: ty.Optional[ty.Tuple[str, ...]] = None
    binary = True
    classifiers_attr_name = "image_contents"
    image_contents = ()
    allowed_classifiers = (ContentsClassifier,)
    multiple_classifiers = True
    exclusive_classifiers = (ImagingModality, AnatomicalEntity, Derivative)

    @extra
    def read_array(self) -> DataArrayType:
        """
        Returns the binary data of the image in a numpy array
        """
        raise NotImplementedError

    @mtime_cached_property
    def data_array(self) -> DataArrayType:
        return self.read_array()

    @extra
    def vox_sizes(self) -> ty.Tuple[float, float, float]:
        """The length of the voxels along each dimension"""
        raise NotImplementedError

    @extra
    def dims(self) -> ty.Tuple[int, int, int]:
        """The dimensions of the image"""
        raise NotImplementedError
