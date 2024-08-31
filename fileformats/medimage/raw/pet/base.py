from fileformats.generic import File


class PetRawData(File):

    binary = True
    # iana_mime = None
    pass


class PetListMode(PetRawData):
    "raw projection data"
    # iana_mime = None
    pass


class PetSinogram(PetRawData):
    "histogrammed projection data in a reconstruction-friendly format"
    # iana_mime = None
    pass


class PetCountRate(PetRawData):
    "number of prompt/random/single events per unit time"
    # iana_mime = None
    pass


class PetNormalisation(PetRawData):
    "normalisation scan or the current cross calibration factor"
    # iana_mime = None
    pass
