import os
import os.path as op
import pydicom
import numpy as np
from fileformats.generic import File, Directory
from .base import MedicalImage

# =====================================================================
# Custom loader functions for different image types
# =====================================================================


class DicomFile(
    File
):  # FIXME: Should extend from MedicalImage, but need to implement header and array

    ext = ".dcm"


class SiemensDicomFile(DicomFile):

    ext = ".IMA"


class Dicom(Directory, MedicalImage):

    content_types = (DicomFile,)
    alternate_names = ("secondary",)

    SERIES_NUMBER_TAG = ("0020", "0011")

    def dcm_files(self):
        return [f for f in os.listdir(self.path) if f.endswith(".dcm")]

    @property
    def data_array(self):
        image_stack = []
        for fname in self.dcm_files(self):
            image_stack.append(pydicom.dcmread(op.join(self.path, fname)).pixel_array)
        return np.asarray(image_stack)

    def load_metadata(self, index=0):
        dcm_files = [f for f in os.listdir(self.path) if f.endswith(".dcm")]
        # TODO: Probably should collate fields that vary across the set of
        #       files in the set into lists
        return pydicom.dcmread(op.join(self.path, dcm_files[index]))

    @property
    def vox_sizes(self):
        return np.array(self.metadata["PixelSpacing"] + [self.metadata["SliceThickness"]])

    @property
    def dims(self):
        return np.array(
            (self.metadata["Rows"], self.metadata["DataColumns"], len(self.dcm_files(self))), datatype=int
        )

    def extract_id(self):
        return int(self.dicom_values([self.SERIES_NUMBER_TAG])[0])

    def dicom_values(self, tags):
        """
        Returns a dictionary with the DICOM header fields corresponding
        to the given tag names

        Parameters
        ----------
        fileset : FileSet
            The file set to extract the DICOM header for
        tags : List[Tuple[str, str]]
            List of DICOM tag values as 2-tuple of strings, e.g.
            [('0080', '0020')]

        Returns
        -------
        dct : Dict[Tuple[str, str], str|int|float]
        """

        def read_header():
            dcm = self.get_header(0)
            return [dcm[t].value for t in tags]

        try:
            if self.fspath:
                # Get the DICOM object for the first file in the self
                dct = read_header()
            else:
                try:
                    # Try to access dicom header details remotely
                    hdr = self.row.dataset.store.dicom_header(self)
                except AttributeError:
                    self.get()  # Fallback to downloading data to read header
                    dct = read_header()
                else:
                    dct = [hdr[t] for t in tags]
        except KeyError as e:
            e.msg = "{} does not have dicom tag {}".format(self, str(e))
            raise e
        return dct


class SiemensDicom(Dicom):

    content_types = (SiemensDicomFile,)
    alternative_names = ("dicom",)
