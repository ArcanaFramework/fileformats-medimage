import pytest
from medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c import get_image as get_dicom
from medimages4tests.dummy.nifti import get_image as get_nifti
from fileformats.core.exceptions import FormatMismatchError
from fileformats.medimage import DicomDir


def test_dicom_identify():
    DicomDir(get_dicom())


def test_dicom_not_identify():
    with pytest.raises(FormatMismatchError, match="No directory paths provided"):
        DicomDir(get_nifti())
