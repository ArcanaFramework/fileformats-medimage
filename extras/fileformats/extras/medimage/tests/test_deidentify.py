import pytest
from fileformats.core.exceptions import FileFormatsExtrasError
from fileformats.medimage import DicomImage, DicomDir, DicomSeries, Nifti1
from medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c import (
    get_image as get_dicom_image,
)
from fileformats.medimage import Vnd_Siemens_Biograph128Vision_Vr20b_PetSinogram


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
    deidentified = dicom.deidentify()
    assert str(deidentified.metadata["PatientName"]) == "Anonymous^Anonymous"


def test_nifti_deidentify():
    nifti = Nifti1.sample()
    deidentified = nifti.deidentify()
    assert nifti is not deidentified
    assert nifti.hash_files() == deidentified.hash_files()


def test_raw_pet_data_deidentify():
    raw_pet = Vnd_Siemens_Biograph128Vision_Vr20b_PetSinogram.sample()
    with pytest.raises(FileFormatsExtrasError):
        raw_pet.deidentify()
