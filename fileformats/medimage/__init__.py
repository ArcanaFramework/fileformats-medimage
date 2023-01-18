from ._version import __version__
from .base import MedicalImage, NeuroImage
from .misc import (  # noqa: F401
    Analyze,
)
from .nifti import (
    Nifti,
    Nifti_Gzip,
    Nifti_Bids,
    Nifti_Gzip_Bids,
)
from .mrtrix import MrtrixImage, MrtrixImageHeader
from .diffusion import (
    DwiEncoding,
    MrtrixTrack,
    Mrtrixgrad,
    Fslgrad,
    Nifti_Fslgrad,
    Nifti_Gzip_Fslgrad,
    Nifti_Bids_Fslgrad,
    Nifti_Gzip_Bids_Fslgrad,
)
from .dicom import (  # noqa: F401
    DicomFile,
    SiemensDicomFile,
    Dicom,
    SiemensDicom,
)
from .raw import (  # noqa: F401
    ListMode,
    Kspace,
    TwixVb,
    CustomKspace,
    Rda,
)

try:
    import fileformats.medimage.converters
except ImportError:
    from warnings import warn
    warn(
        f"could not import converters for {__name__}  module, please install "
        "fileformats-medimage[converters] package if converters are desired"
    )

