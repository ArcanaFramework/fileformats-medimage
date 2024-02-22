import itertools
import pytest
from medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c import get_image as get_dicom
from medimages4tests.dummy.nifti import get_image as get_nifti
from fileformats.core.exceptions import FormatMismatchError
from fileformats.core import from_paths
from fileformats.medimage import DicomDir, DicomSeries


def test_dicom_identify():
    DicomDir(get_dicom())


def test_dicom_not_identify():
    with pytest.raises(FormatMismatchError, match="No directory paths provided"):
        DicomDir(get_nifti())


def test_series_from_paths(tmp_path):
    filesets = [
        DicomSeries.sample(tmp_path, seed=1),
        DicomSeries.sample(tmp_path, seed=2),
        DicomSeries.sample(tmp_path, seed=3),
    ]

    fspaths = list(itertools.chain(*(f.fspaths for f in filesets)))

    detected = from_paths(fspaths, DicomSeries)

    assert set(detected) == set(filesets)


def test_dicom_series_metadata(tmp_path):
    series = DicomSeries.sample(tmp_path)

    # Check series number is not a list
    assert not isinstance(series.metadata["SeriesNumber"], list)
    # check the SOP Instance ID has been converted into a list
    assert isinstance(series.metadata["SOPInstanceUID"], list)
