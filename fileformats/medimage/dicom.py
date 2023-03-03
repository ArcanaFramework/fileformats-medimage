import numpy as np
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

    SERIES_NUMBER_TAG = ("0020", "0011")

    def data_array(self):
        import pydicom

        image_stack = []
        for dcm_file in self.contents:
            image_stack.append(pydicom.dcmread(dcm_file).pixel_array)
        return np.asarray(image_stack)

    def load_metadata(self, index=0, specific_tags=None):
        import pydicom

        # TODO: Probably should collate fields that vary across the set of
        #       files in the set into lists
        return pydicom.dcmread(list(self.contents)[index], specific_tags=specific_tags)

    @property
    def vox_sizes(self):
        return np.array(
            self.metadata["PixelSpacing"] + [self.metadata["SliceThickness"]]
        )

    @property
    def dims(self):
        return np.array(
            (
                self.metadata["Rows"],
                self.metadata["DataColumns"],
                len(list(self.contents)),
            ),
            datatype=int,
        )

    def extract_id(self):
        return int(self.load_metadata(specific_tags=[self.SERIES_NUMBER_TAG])[0])


class DicomDir(DicomCollection, Directory):
    pass


class DicomSet(DicomCollection, TypedSet):
    pass
