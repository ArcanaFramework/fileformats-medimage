import pytest
import pydicom
from pathlib import Path
from fileformats.core.exceptions import FileFormatsExtrasError
from medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c import (
    get_image as get_dicom_image,
)

from fileformats.medimage import DicomDir, DicomImage, DicomSeries, Nifti1


@pytest.fixture(params=["image", "dir", "series"])
def dicom(request):
    dicom_dir = get_dicom_image(first_name="John", last_name="Doe")
    dicom_files = sorted(p for p in dicom_dir.iterdir() if p.suffix == ".dcm")
    if request.param == "image":
        return DicomImage(dicom_files[0])
    elif request.param == "dir":
        return DicomDir(dicom_dir)
    else:
        return DicomSeries(dicom_files)


@pytest.fixture
def single_dicom():
    dicom_dir = get_dicom_image(first_name="John", last_name="Doe")
    dcm_file = next(p for p in dicom_dir.iterdir() if p.suffix == ".dcm")
    return DicomImage(dcm_file)


# ---------------------------------------------------------------------------
# Tests against bundled recipe.dicom (integration)
# ---------------------------------------------------------------------------


def test_deidentify_patient_name(dicom, tmp_path):
    """PatientName should be replaced with original PatientID."""
    orig_patient_id = dicom.metadata["PatientID"]
    deidentified = dicom.deidentify(tmp_path)
    assert str(deidentified.metadata["PatientName"]) == orig_patient_id


def test_deidentify_patient_id(dicom, tmp_path):
    """PatientID should become PatientID-AcquisitionTime."""
    orig_id = dicom.metadata["PatientID"]
    orig_time = dicom.metadata["AcquisitionTime"]
    deidentified = dicom.deidentify(tmp_path)
    assert deidentified.metadata["PatientID"] == f"{orig_id}-{orig_time}"


def test_deidentify_birth_date(dicom, tmp_path):
    """PatientBirthDate should keep year, set to Jan 1."""
    orig_year = dicom.metadata["PatientBirthDate"][:4]
    deidentified = dicom.deidentify(tmp_path)
    assert deidentified.metadata["PatientBirthDate"] == f"{orig_year}0101"


def test_deidentify_patient_comments(dicom, tmp_path):
    """PatientComments should contain Project/Subject/Session mapping."""
    orig_id = dicom.metadata["PatientID"]
    orig_time = dicom.metadata["AcquisitionTime"]
    orig_ref_phys = str(dicom.metadata["ReferringPhysicianName"])
    deidentified = dicom.deidentify(tmp_path)
    comments = deidentified.metadata["PatientComments"]
    assert f"Project={orig_ref_phys}" in comments
    assert f"Subject={orig_id}" in comments
    assert f"Session={orig_id}-{orig_time}" in comments


def test_deidentify_removes_institution(dicom, tmp_path):
    """Institution fields should be removed."""
    assert dicom.metadata["InstitutionAddress"]
    deidentified = dicom.deidentify(tmp_path)
    assert "InstitutionAddress" not in deidentified.metadata


def test_deidentify_removes_station(dicom, tmp_path):
    """StationName should be removed."""
    deidentified = dicom.deidentify(tmp_path)
    assert "StationName" not in deidentified.metadata


def test_deidentify_preserves_uids(dicom, tmp_path):
    """Study/Series/SOP UIDs should be preserved."""
    orig_study = dicom.metadata["StudyInstanceUID"]
    orig_series = dicom.metadata["SeriesInstanceUID"]
    deidentified = dicom.deidentify(tmp_path)
    assert deidentified.metadata["StudyInstanceUID"] == orig_study
    assert deidentified.metadata["SeriesInstanceUID"] == orig_series


def test_deidentify_marks_as_deidentified(dicom, tmp_path):
    """PatientIdentityRemoved should be set to YES."""
    deidentified = dicom.deidentify(tmp_path)
    assert deidentified.metadata["PatientIdentityRemoved"] == "YES"


# ---------------------------------------------------------------------------
# Custom variable builders
# ---------------------------------------------------------------------------


def test_custom_variable_builders(single_dicom, tmp_path):
    """Caller-supplied variable_builders should override defaults."""
    custom_builders = {
        "anon_patient_name": lambda _ds: "CUSTOM_NAME",
    }
    deidentified = single_dicom.deidentify(
        tmp_path, variable_builders=custom_builders
    )
    assert str(deidentified.metadata["PatientName"]) == "CUSTOM_NAME"


def test_custom_variable_builders_preserve_other_defaults(single_dicom, tmp_path):
    """Overriding one builder should not affect other defaults."""
    custom_builders = {
        "anon_patient_name": lambda _ds: "CUSTOM_NAME",
    }
    orig_year = single_dicom.metadata["PatientBirthDate"][:4]
    deidentified = single_dicom.deidentify(
        tmp_path, variable_builders=custom_builders
    )
    # Birth date should still use the default builder
    assert deidentified.metadata["PatientBirthDate"] == f"{orig_year}0101"


# ---------------------------------------------------------------------------
# Custom recipe
# ---------------------------------------------------------------------------


def test_custom_recipe_path(single_dicom, tmp_path):
    """A custom recipe file should be used instead of the default."""
    recipe_file = tmp_path / "custom.dicom"
    recipe_file.write_text(
        "FORMAT dicom\n\n%header\nREPLACE PatientName CUSTOM_FROM_RECIPE\n"
    )
    out_dir = tmp_path / "output"
    deidentified = single_dicom.deidentify(out_dir, spec=str(recipe_file))
    assert str(deidentified.metadata["PatientName"]) == "CUSTOM_FROM_RECIPE"


# ---------------------------------------------------------------------------
# Output structure
# ---------------------------------------------------------------------------


def test_deidentify_creates_output_dir(single_dicom, tmp_path):
    """Output directory should be created if it doesn't exist."""
    out_dir = tmp_path / "nested" / "output"
    single_dicom.deidentify(out_dir)
    assert out_dir.is_dir()


def test_deidentify_output_is_valid_dicom(single_dicom, tmp_path):
    """Output file should be a valid DICOM that pydicom can read."""
    deidentified = single_dicom.deidentify(tmp_path)
    ds = pydicom.dcmread(str(deidentified.fspath))
    assert ds.PatientName is not None


# ---------------------------------------------------------------------------
# Nifti (no deid support)
# ---------------------------------------------------------------------------


def test_nifti_deidentify(tmp_path):
    nifti = Nifti1.sample()
    with pytest.raises(FileFormatsExtrasError):
        nifti.deidentify(tmp_path)
