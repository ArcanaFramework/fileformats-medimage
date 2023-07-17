import pytest
from medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c import get_image as get_dicom
from medimages4tests.dummy.nifti import get_image as get_nifti
from fileformats.core.exceptions import FormatMismatchError
from fileformats.medimage import Nifti1


def test_nifti_identify():
    Nifti1(get_nifti())


def test_nifti_not_identify():
    with pytest.raises(FormatMismatchError, match="No matching files with extensions"):
        Nifti1(get_dicom())
