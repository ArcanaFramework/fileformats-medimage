import pytest
from fileformats.medimage import DicomSeries, DicomDir
from conftest import OLD_MRTRIX_VERSION


@pytest.mark.xfail(condition=OLD_MRTRIX_VERSION, reason="Old MRtrix version")
def test_dicom_series_metadata(tmp_path):
    series = DicomSeries.sample(tmp_path)

    # Check series number is not a list
    assert not isinstance(series.metadata["SeriesNumber"], list)
    # check the SOP Instance ID has been converted into a list
    assert isinstance(series.metadata["SOPInstanceUID"], list)


@pytest.mark.xfail(condition=OLD_MRTRIX_VERSION, reason="Old MRtrix version")
def test_dicom_dir_metadata(tmp_path):
    series = DicomDir.sample(tmp_path)

    # Check series number is not a list
    assert not isinstance(series.metadata["SeriesNumber"], list)
    # check the SOP Instance ID has been converted into a list
    assert isinstance(series.metadata["SOPInstanceUID"], list)
