from .. import ContentsClassifier


class Derivative(ContentsClassifier):
    """An image type that is derived from other images"""


class Mask(Derivative):
    """A binary image that is multiplied with a real-valued image to select sections
    of the image for analysis"""


class FibreOrientationDistribution(Derivative):
    pass


FOD = FibreOrientationDistribution
