import sys
import typing as ty
from pathlib import Path
from fileformats.core import FileSet, extra
from fileformats.medimage import MedicalImagingData
from fileformats.generic import BinaryFile

if sys.version_info >= (3, 12):
    from typing import Self
else:
    from typing_extensions import Self


class PetRawData(BinaryFile, MedicalImagingData):
    """Base class for raw PET data files"""

    @extra
    def deidentify(
        self,
        out_dir: ty.Optional[Path] = None,
        new_stem: ty.Optional[str] = None,
        copy_mode: FileSet.CopyMode = FileSet.CopyMode.copy,
    ) -> Self:
        """Returns a new copy of the data with any subject-identifying information
        stripped from the from the data header"""
        raise NotImplementedError


class PetListMode(PetRawData):
    "raw projection data"


class PetSinogram(PetRawData):
    "histogrammed projection data in a reconstruction-friendly format"


class PetCountRate(PetRawData):
    "number of prompt/random/single events per unit time"


class PetNormalisation(PetRawData):
    "normalisation scan or the current cross calibration factor"
