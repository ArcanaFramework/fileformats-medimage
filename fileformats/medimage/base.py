import typing as ty
import logging
from fileformats.core import hook, FileSet
from fileformats.core.mixin import WithClassifiers
from .contents import ContentsClassifier
from .contents.imaging.modality import ImagingModality
from .contents.imaging.derivatives import Derivative
from .contents.anatomical_entity.material_anatomical_entity import AnatomicalEntity

logger = logging.getLogger("fileformats")


# =====================================================================
# Custom loader functions for different image types
# =====================================================================


class MedicalImage(WithClassifiers, FileSet):

    iana_mime: ty.Optional[str] = None
    INCLUDE_HDR_KEYS = None
    IGNORE_HDR_KEYS = None
    binary = True
    classifiers_attr_name = "image_contents"
    image_contents = ()
    allowed_classifiers = (ContentsClassifier,)
    multiple_classifiers = True
    exclusive_classifiers = (ImagingModality, AnatomicalEntity, Derivative)

    @hook.extra
    def read_array(self) -> "numpy.ndarray":  # noqa
        """
        Returns the binary data of the image in a numpy array
        """
        raise NotImplementedError

    @hook.extra
    def vox_sizes(self) -> ty.Tuple[float, float, float]:
        """The length of the voxels along each dimension"""
        raise NotImplementedError

    @hook.extra
    def dims(self) -> ty.Tuple[int, int, int]:
        """The dimensions of the image"""
        raise NotImplementedError
