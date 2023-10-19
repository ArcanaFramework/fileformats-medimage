from .base import (
    PetRawData,
    PetListMode,
    PetSinogram,
    PetCountRate,
    PetNormalisation,
)


class Vnd_Siemens_PetRawData(PetRawData):

    iana_mime = None
    ext = ".ptd"


class Vnd_Siemens_PetListMode(Vnd_Siemens_PetRawData, PetListMode):
    pass


class Vnd_Siemens_PetSinogram(Vnd_Siemens_PetRawData, PetSinogram):
    "histogrammed projection data in a reconstruction-friendly format"


class Vnd_Siemens_PetCountRate(Vnd_Siemens_PetRawData, PetCountRate):
    "number of prompt/random/single events per unit time"


class Vnd_Siemens_PetNormalisation(Vnd_Siemens_PetRawData, PetNormalisation):
    "normalisation scan or the current cross calibration factor"
