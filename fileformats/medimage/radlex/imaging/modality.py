from fileformats.core import ClassifierCategory


class ImagingModality(ClassifierCategory):
    pass


class CombinedModalities(ImagingModality):
    pass


class DualEnergyXrayAbsorptiometry(ImagingModality):
    pass


class Fluoroscopy(ImagingModality):
    pass


class MagneticResonanceImaging(ImagingModality):
    pass


class MagneticResonanceSpectroscopy(ImagingModality):
    pass


class NuclearMedicineImaging(ImagingModality):
    pass


class PanographicRadiograph(ImagingModality):
    pass


class ProjectionRadiography(ImagingModality):
    pass


class Spectroscopy(ImagingModality):
    pass


class Tomography(ImagingModality):
    pass


class Ultrasound(ImagingModality):
    pass


class DiffusionTensorImaging(MagneticResonanceImaging):
    pass


class DynamicContrast(MagneticResonanceImaging):
    pass


class EnhancedMagneticResonanceImaging(MagneticResonanceImaging):
    pass


class FunctionalMagneticResonanceImaging(MagneticResonanceImaging):
    pass


class MagneticResonanceAngiography(MagneticResonanceImaging):
    pass
