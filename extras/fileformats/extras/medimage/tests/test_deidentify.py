import pytest
from fileformats.medimage import DicomImage, DicomDir, DicomSeries, Nifti1
from medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c import (
    get_image as get_dicom_image,
)


@pytest.fixture(params=["image", "dir", "series"])
def dicom(request):
    dicom_dir = get_dicom_image(first_name="John", last_name="Doe")
    dicom_files = (p for p in dicom_dir.iterdir() if p.suffix == ".dcm")
    if request.param == "image":
        return DicomImage(next(dicom_files))
    elif request.param == "dir":
        return DicomDir(dicom_dir)
    else:
        return DicomSeries(dicom_files)


def test_deidentify_dicom(dicom):
    assert str(dicom.metadata["PatientName"]) == "Doe^John"
    assert dicom.metadata["InstitutionAddress"]
    assert not dicom.metadata["PatientBirthDate"].endswith("0101")
    deidentified = dicom.deidentify()
    assert str(deidentified.metadata["PatientName"]) == "Anonymous^Anonymous"
    assert deidentified.metadata["InstitutionAddress"] == ""
    assert deidentified.metadata["PatientBirthDate"] == "19800101"


def test_nifti_deidentify():
    nifti = Nifti1.sample()
    deidentified = nifti.deidentify()
    assert nifti is not deidentified
    assert nifti.hash_files() == deidentified.hash_files()
