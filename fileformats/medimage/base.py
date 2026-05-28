import os
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
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if ty.TYPE_CHECKING:
    import numpy.typing  # noqa: F401


# =====================================================================
# Custom loader functions for different image types
# =====================================================================

DataArrayType: TypeAlias = (
    ty.Any
)  # In Py<3.9 this is problematic "numpy.typing.NDArray[typing.Union[numpy.floating[typing.Any], numpy.integer[typing.Any]]]"


class MedicalImagingData(FileSet):
    """Base class for all medical imaging data including pre-image raw data and
    associated data"""

    contains_phi: bool = True

    @extra
    def deidentify(
        self,
        spec: ty.Any = None,
        out_dir: os.PathLike[str] | None = None,
    ) -> tuple[Self, ty.Mapping[str, ty.Any]]:
        """
        Deidentifies the image by stripping any subject-identifying information from the
        image header. The exact implementation of this method will depend on the
        specific image format and the type of identifying information that is present. The
        output files should be named with a new file path(s) that is derived from the metadata,
        such that it doesn't contain any subject-identifying information within it.

        Parameters
        ----------
        spec: Any, optional
            A specification for the deidentification process, which may include details on
            which fields to remove or how to handle certain types of data. The exact
            structure of this specification will depend on the specific image format and the
            requirements of the deidentification process.
        out_dir: PathLike[str], optional
            An optional directory where the deidentified image should be saved. If not
            provided, the deidentified image may be saved in a temporary directory

        Returns
        -------
        Self
            A new instance of the image with any subject-identifying information stripped from
            the image header.
        dict[str, Any]
            A JSON-like nested dictionary containing the original values from the header that
            were stripped/modified during the deidentification process.
        """
        raise NotImplementedError


class MedicalImage(WithClassifiers, MedicalImagingData):

    INCLUDE_HDR_KEYS: ty.Optional[ty.Tuple[str, ...]] = None
    IGNORE_HDR_KEYS: ty.Optional[ty.Tuple[str, ...]] = None
    binary = True
    classifiers_attr_name = "image_contents"
    image_contents = ()
    allowed_classifiers = (ContentsClassifier,)
    exclusive_classifiers = (ImagingModality, AnatomicalEntity, Derivative)

    @extra
    def read_array(self) -> DataArrayType:
        """
        Returns the binary data of the image in a numpy array
        """

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
