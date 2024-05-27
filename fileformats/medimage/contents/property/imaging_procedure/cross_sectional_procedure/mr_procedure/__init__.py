from .. import CrossSectionalProcedure
from fileformats.medimage.contents.imaging.modality import MagneticResonanceImaging


class MrProcedure(CrossSectionalProcedure, MagneticResonanceImaging):
    pass
