from fileformats.core import mark
from fileformats.generic import Directory, TypedSet
from fileformats.misc import Dicom
from .base import MedicalImage

# =====================================================================
# Custom loader functions for different image types
# =====================================================================


class DicomCollection(MedicalImage):
    """Base class for collections of DICOM files, which can either be stored within a
    directory (DicomDir) or presented as a flat list (DicomSet)
    """

    content_types = (Dicom,)
    iana_mime = None

    @mark.extra
    def series_number(self):
        raise NotImplementedError


class DicomDir(DicomCollection, Directory):
    pass


class DicomSet(DicomCollection, TypedSet):
    pass
