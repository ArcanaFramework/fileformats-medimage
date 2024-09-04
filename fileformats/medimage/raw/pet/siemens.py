from fileformats.generic import TypedSet
from .base import (
    PetRawData,
    PetListMode,
    PetSinogram,
    PetCountRate,
    PetNormalisation,
)


class Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData(PetRawData):
    # iana_mime = None
    pass
    ext = ".ptd"


class Vnd_Siemens_Biograph128Vision_Vr20b_PetListMode(
    Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData, PetListMode
):
    pass


class Vnd_Siemens_Biograph128Vision_Vr20b_PetSinogram(
    Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData, PetSinogram
):
    "histogrammed projection data in a reconstruction-friendly format"


class Vnd_Siemens_Biograph128Vision_Vr20b_PetCountRate(
    Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData, PetCountRate
):
    "number of prompt/random/single events per unit time"


class Vnd_Siemens_Biograph128Vision_Vr20b_PetNormalisation(
    Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData, PetNormalisation
):
    "normalisation scan or the current cross calibration factor"


class Vnd_Siemens_Biograph128Vision_Vr20b_PetSinogramSeries(TypedSet):
    "Series of sinogram images"
    content_types = (Vnd_Siemens_Biograph128Vision_Vr20b_PetSinogram,)
