import os
import logging
import tempfile
from pathlib import Path
import pytest
try:
    from pydra import set_input_validator
except ImportError:
    pass
else:
    set_input_validator(True)
from fileformats.medimage.dicom import DicomDir

try:
    import pydra.tasks.mrtrix3.v3_0  # noqa
except ImportError:
    OLD_MRTRIX_VERSION = True
else:
    OLD_MRTRIX_VERSION = False

# Set DEBUG logging for unittests

log_level = logging.WARNING

logger = logging.getLogger("arcana")
logger.setLevel(log_level)

sch = logging.StreamHandler()
sch.setLevel(log_level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sch.setFormatter(formatter)
logger.addHandler(sch)


@pytest.fixture(scope="session")
def dummy_t1w_dicom():
    import medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c as module

    return DicomDir(module.get_image())


@pytest.fixture(scope="session")
def dummy_magfmap_dicom():
    import medimages4tests.dummy.dicom.mri.fmap.siemens.skyra.syngo_d13c as module

    return DicomDir(module.get_image())


@pytest.fixture(scope="session")
def dummy_dwi_dicom():
    import medimages4tests.dummy.dicom.mri.dwi.siemens.skyra.syngo_d13c as module

    return DicomDir(module.get_image())


@pytest.fixture(scope="session")
def dummy_mixedfmap_dicom():
    import medimages4tests.dummy.dicom.mri.fmap.ge.discovery_mr888.dv26_0_r05_2008a as module

    return DicomDir(module.get_image())


@pytest.fixture(scope="session")
def dummy_dwi_dicom():
    import medimages4tests.dummy.dicom.mri.dwi.siemens.skyra.syngo_d13c as module

    return DicomDir(module.get_image())

# For debugging in IDE's don't catch raised exceptions and let the IDE
# break at it
if os.getenv("_PYTEST_RAISE", "0") != "0":

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call):
        raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo):
        raise excinfo.value


@pytest.fixture
def work_dir():
    work_dir = tempfile.mkdtemp()
    return Path(work_dir)
