from fileformats.generic import BinaryFile


class PetRawData(BinaryFile):
    """Base class for raw PET data files"""


class PetListMode(PetRawData):
    "raw projection data"


class PetSinogram(PetRawData):
    "histogrammed projection data in a reconstruction-friendly format"


class PetCountRate(PetRawData):
    "number of prompt/random/single events per unit time"


class PetNormalisation(PetRawData):
    "normalisation scan or the current cross calibration factor"
