import typing as ty
import logging
from fileformats.core import extra, FileSet
from fileformats.core.mixin import WithClassifiers
from .contents import ContentsClassifier
from .contents.imaging.modality import ImagingModality
from .contents.imaging.derivatives import Derivative
from .contents.anatomical_entity import AnatomicalEntity

logger = logging.getLogger("fileformats")

if ty.TYPE_CHECKING:
    import numpy as np
    import numpy.typing


# =====================================================================
# Custom loader functions for different image types
# =====================================================================


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
    def read_array(self) -> numpy.typing.NDArray[ty.Union[np.float_, np.int_]]:  # noqa
        """
        Returns the binary data of the image in a numpy array
        """
        raise NotImplementedError

    @extra
    def vox_sizes(self) -> ty.Tuple[float, float, float]:
        """The length of the voxels along each dimension"""
        raise NotImplementedError

    @extra
    def dims(self) -> ty.Tuple[int, int, int]:
        """The dimensions of the image"""
        raise NotImplementedError
