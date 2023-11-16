from fileformats.medimage import DicomSeries, DicomDir


def test_dicom_series_metadata(tmp_path):
    series = DicomSeries.sample(tmp_path)

    # Check series number is not a list
    assert not isinstance(series["SeriesNumber"], list)
    # check the SOP Instance ID has been converted into a list
    assert isinstance(series["SOPInstanceUID"], list)


def test_dicom_dir_metadata(tmp_path):
    series = DicomDir.sample(tmp_path)

    # Check series number is not a list
    assert not isinstance(series["SeriesNumber"], list)
    # check the SOP Instance ID has been converted into a list
    assert isinstance(series["SOPInstanceUID"], list)
