import pytest
from fileformats.medimage import (
    NiftiGzX,
    NiftiGzXBvec,
    Analyze,
)
from logging import getLogger
from conftest import OLD_MRTRIX_VERSION


logger = getLogger("fileformats")


@pytest.mark.xfail(reason="refactoring of side car handling incomplete")
def test_dicom_to_nifti(dummy_t1w_dicom):

    nifti_gz_x = NiftiGzX.convert(dummy_t1w_dicom)
    assert nifti_gz_x.metadata["EchoTime"] == 0.00207


@pytest.mark.xfail(reason="refactoring of side car handling incomplete")
def test_dicom_to_nifti_select_echo(dummy_magfmap_dicom):

    nifti_gz_x_e1 = NiftiGzX.convert(dummy_magfmap_dicom, file_postfix="_e1")
    nifti_gz_x_e2 = NiftiGzX.convert(dummy_magfmap_dicom, file_postfix="_e2")
    assert nifti_gz_x_e1.metadata["EchoNumber"] == 1
    assert nifti_gz_x_e2.metadata["EchoNumber"] == 2


@pytest.mark.xfail(condition=OLD_MRTRIX_VERSION, reason="Old MRtrix version")
def test_dicom_to_nifti_select_suffix(dummy_mixedfmap_dicom):

    nifti_gz_x_ph = NiftiGzX.convert(dummy_mixedfmap_dicom, file_postfix="_ph")
    nifti_gz_x_imaginary = NiftiGzX.convert(
        dummy_mixedfmap_dicom, file_postfix="_imaginary"
    )
    nifti_gz_x_real = NiftiGzX.convert(dummy_mixedfmap_dicom, file_postfix="_real")

    assert list(nifti_gz_x_ph.dims()) == [256, 256, 60]
    assert list(nifti_gz_x_imaginary.dims()) == [256, 256, 60]
    assert list(nifti_gz_x_real.dims()) == [256, 256, 60]


# @pytest.mark.xfail(condition=OLD_MRTRIX_VERSION, reason="Old MRtrix version")
@pytest.mark.xfail(reason="Waiting on next Pydra release")
def test_dicom_to_nifti_with_extract_volume(dummy_dwi_dicom):

    nifti_gz_x_e1 = NiftiGzX.convert(dummy_dwi_dicom, extract_volume=30)
    assert nifti_gz_x_e1.metadata["dim"][0] == 3


@pytest.mark.xfail(reason="refactoring of side car handling incomplete")
def test_dicom_to_nifti_with_jq_edit(dummy_t1w_dicom):

    nifti_gz_x = NiftiGzX.convert(dummy_t1w_dicom, side_car_jq=".EchoTime *= 1000")
    assert nifti_gz_x.metadata["EchoTime"] == 2.07


@pytest.mark.xfail(condition=OLD_MRTRIX_VERSION, reason="Old MRtrix version")
def test_dicom_to_niftix_with_fslgrad(dummy_dwi_dicom):

    logger.debug("Performing FSL grad conversion")

    nifti_gz_x_fsgrad = NiftiGzXBvec.convert(dummy_dwi_dicom)

    bvec_mags = [
        (v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
        for v in nifti_gz_x_fsgrad.encoding.directions
        if any(v)
    ]

    assert all(b in (0.0, 3000.0) for b in nifti_gz_x_fsgrad.encoding.b_values)
    assert len(bvec_mags) == 60
    assert all(abs(1 - m) < 1e5 for m in bvec_mags)


# @pytest.mark.xfail(condition=OLD_MRTRIX_VERSION, reason="Old MRtrix version")
@pytest.mark.xfail(reason="Waiting on next Pydra release")
def test_dicom_to_nifti_as_4d(dummy_t1w_dicom):

    nifti_gz_x_e1 = NiftiGzX.convert(dummy_t1w_dicom, to_4d=True)
    assert nifti_gz_x_e1.metadata["dim"][0] == 4


@pytest.mark.xfail(condition=OLD_MRTRIX_VERSION, reason="Old MRtrix version")
def test_dicom_to_analyze(dummy_t1w_dicom):
    Analyze.convert(dummy_t1w_dicom)
