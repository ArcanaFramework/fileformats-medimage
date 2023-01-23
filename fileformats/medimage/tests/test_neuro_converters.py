from fileformats.medimage import (
    Nifti_Gzip_Bids,
    Nifti_Gzip_Bids_Fslgrad,
    Nifti_Fslgrad,
    MrtrixImage,
    MrtrixImageHeader,
    Analyze,
)
from logging import getLogger


logger = getLogger("fileformats")


def test_dicom_to_nifti(dummy_t1w_dicom):

    nifti_gz_x = Nifti_Gzip_Bids.convert(dummy_t1w_dicom)
    nifti_gz_x.validate()
    assert nifti_gz_x.metadata["EchoTime"] == 0.00207


def test_dicom_to_nifti_select_echo(dummy_magfmap_dicom):

    nifti_gz_x_e1 = Nifti_Gzip_Bids.convert(dummy_magfmap_dicom, file_postfix="_e1")
    nifti_gz_x_e2 = Nifti_Gzip_Bids.convert(dummy_magfmap_dicom, file_postfix="_e2")
    nifti_gz_x_e1.validate()
    nifti_gz_x_e2.validate()
    assert nifti_gz_x_e1.metadata["EchoNumber"] == 1
    assert nifti_gz_x_e2.metadata["EchoNumber"] == 2


def test_dicom_to_nifti_select_suffix(dummy_mixedfmap_dicom):

    nifti_gz_x_ph = Nifti_Gzip_Bids.convert(dummy_mixedfmap_dicom, file_postfix="_ph")
    nifti_gz_x_imaginary = Nifti_Gzip_Bids.convert(
        dummy_mixedfmap_dicom, file_postfix="_imaginary"
    )
    nifti_gz_x_real = Nifti_Gzip_Bids.convert(
        dummy_mixedfmap_dicom, file_postfix="_real"
    )

    nifti_gz_x_ph.validate()
    nifti_gz_x_imaginary.validate()
    nifti_gz_x_real.validate()

    assert list(nifti_gz_x_ph.dims) == [256, 256, 60]
    assert list(nifti_gz_x_imaginary.dims) == [256, 256, 60]
    assert list(nifti_gz_x_real.dims) == [256, 256, 60]


def test_dicom_to_nifti_with_extract_volume(dummy_dwi_dicom):

    nifti_gz_x_e1 = Nifti_Gzip_Bids.convert(dummy_dwi_dicom, extract_volume=30)
    nifti_gz_x_e1.validate()
    assert nifti_gz_x_e1.metadata["dim"][0] == 3


def test_dicom_to_nifti_with_jq_edit(dummy_t1w_dicom):

    nifti_gz_x = Nifti_Gzip_Bids.convert(
        dummy_t1w_dicom, side_car_jq=".EchoTime *= 1000"
    )
    nifti_gz_x.validate()
    assert nifti_gz_x.metadata["EchoTime"] == 2.07


def test_dicom_to_niftix_with_fslgrad(dummy_dwi_dicom):

    logger.debug("Performing FSL grad conversion")

    nifti_gz_x_fsgrad = Nifti_Gzip_Bids_Fslgrad.convert(dummy_dwi_dicom)
    nifti_gz_x_fsgrad.validate()

    bvec_mags = [
        (v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
        for v in nifti_gz_x_fsgrad.grads.dirs
        if any(v)
    ]

    assert all(b in (0.0, 3000.0) for b in nifti_gz_x_fsgrad.grads.b)
    assert len(bvec_mags) == 60
    assert all(abs(1 - m) < 1e5 for m in bvec_mags)


# @pytest.mark.skip("Mrtrix isn't installed in test environment yet")
def test_dicom_to_nifti_as_4d(dummy_t1w_dicom):

    nifti_gz_x_e1 = Nifti_Gzip_Bids.convert(dummy_t1w_dicom, to_4d=True)
    nifti_gz_x_e1.validate()
    assert nifti_gz_x_e1.metadata["dim"][0] == 4


# @pytest.mark.xfail(reason="not sure what the reason is at this stage, might be bug in Pydra")
def test_nifti_to_mrtrix(dummy_dwi_dicom):
    nifti_fsgrad = Nifti_Fslgrad.convert(dummy_dwi_dicom)
    nifti_fsgrad.validate()
    mif = MrtrixImage.convert(nifti_fsgrad)
    mif.validate()
    mih = MrtrixImageHeader.convert(nifti_fsgrad)
    mih.validate()


def test_dicom_to_mrtrix_image(dummy_dwi_dicom):
    mif = MrtrixImage.convert(dummy_dwi_dicom)
    mif.validate()


def test_dicom_to_mrtrix_image_header(dummy_dwi_dicom):
    mih = MrtrixImageHeader.convert(dummy_dwi_dicom)
    mih.validate()


def test_dicom_to_analyze(dummy_t1w_dicom):
    analyze = Analyze.convert(dummy_t1w_dicom)
    analyze.validate()
