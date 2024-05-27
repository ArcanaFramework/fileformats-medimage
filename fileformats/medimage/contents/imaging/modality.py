from .. import ContentsClassifier


class ImagingModality(ContentsClassifier):
    ontology_link = "http://www.radlex.org/RID/RID10311"
    description = "Form of imaging that depends on the way the image is produced"
    dicom_modality = None


class CombinedModalities(ImagingModality):
    ontology_link = "http://www.radlex.org/RID/RID49580"
    description = (
        "These are cases where 2 different modalities are "
        "performed in the same imaging setup without moving the "
        "patient. These classes were created as sets, with the "
        "individual modalities as the set members. Any reasoning "
        "involving modality should accommodate this."
    )


class DualEnergyXrayAbsorptiometry(ImagingModality):
    ontology_link = "http://www.radlex.org/RID/RID10363"
    description = None


class Fluoroscopy(ImagingModality):
    ontology_link = "http://www.radlex.org/RID/RID10361"
    description = None


class MrFluoroscopy(Fluoroscopy):
    ontology_link = "http://www.radlex.org/RID/RID10319"
    description = (
        "Non-invasive method of vascular imaging and determination "
        "of internal anatomy without injection of contrast media or "
        "radiation exposure. The technique is used especially in "
        "cerebral angiography as well as for studies of other vascular "
        "structures. [MeSH]"
    )


class RadioFluoroscopy(Fluoroscopy):
    ontology_link = "http://www.radlex.org/RID/RID45709"
    description = (
        "Production of an image when x-rays strike a fluorescent screen. [MeSH]"
    )


class MagneticResonanceImaging(ImagingModality):
    ontology_link = "http://www.radlex.org/RID/RID10312"
    description = (
        "Non-invasive method of demonstrating internal anatomy "
        "based on the principle that atomic nuclei in a strong "
        "magnetic field absorb pulses of radiofrequency energy and "
        "emit them as radiowaves which can be reconstructed into "
        "computerized images. The concept includes proton spin "
        "tomographic techniques. [MeSH]"
    )
    dicom_modality = "MR"


class DiffusionMagneticResonanceImaging(MagneticResonanceImaging):
    ontology_link = "http://www.radlex.org/RID/RID38778"
    description = None


class DiffusionTensorImaging(DiffusionMagneticResonanceImaging):
    ontology_link = "http://www.radlex.org/RID/RID38778"
    description = None


class DynamicContrast(MagneticResonanceImaging):
    ontology_link = "http://www.radlex.org/RID/RID49531"
    description = (
        "An imaging method with a timed series of T1-weighted "
        "images used to detect and measure signal intensity "
        "change (enhancement) over time following administration "
        "of intravenous contrast agent to noninvasively access "
        "tissue vascular characteristics."
    )


class EnhancedMagneticResonanceImaging(MagneticResonanceImaging):
    pass


class FunctionalMagneticResonanceImaging(MagneticResonanceImaging):
    ontology_link = "http://www.radlex.org/RID/RID10317"
    description = None


class MagneticResonanceAngiography(MagneticResonanceImaging):
    ontology_link = "http://www.radlex.org/RID/RID10319"
    description = None


class MagneticResonanceSpectroscopy(ImagingModality):
    ontology_link = "http://www.radlex.org/RID/RID10315"
    description = (
        "	Spectroscopic method of measuring the magnetic moment of "
        "elementary particles such as atomic nuclei, protons or "
        "electrons. It is employed in clinical applications such as "
        "nmr tomography (magnetic resonance imaging). [MeSH]"
    )


class NuclearMedicineImaging(ImagingModality):
    ontology_link = "http://www.radlex.org/RID/RID10330"
    description = None
    dicom_modality = "NM"


class PositronEmissionTomography(NuclearMedicineImaging):
    ontology_link = "http://www.radlex.org/RID/RID10337"
    description = (
        "An imaging technique using compounds labelled with "
        "short-lived positron-emitting radionuclides (such as "
        "carbon-11, nitrogen-13, oxygen-15 and fluorine-18) to "
        "measure cell metabolism. It has been useful in study of "
        "soft tissues such as cancer; cardiovascular system; and "
        "brain. SPECT is closely related to PET, but uses isotopes "
        "with longer half-lives and resolution is lower. [MeSH]"
    )
    dicom_modality = "PT"


class PanographicRadiograph(ImagingModality):
    ontology_link = "http://www.radlex.org/RID/RID10360"
    description = None
    dicom_modality = "PX"


class ProjectionRadiography(ImagingModality):
    ontology_link = "http://www.radlex.org/RID/RID10345"
    description = (
        "Examination of any part of the body for diagnostic purposes "
        "by means of roentgen rays, recording the image on a "
        "sensitized surface (such as photographic film). [MeSH]"
    )


class ComputedRadiography(ProjectionRadiography):
    ontology_link = "http://www.radlex.org/RID/RID10349"
    dicom_modality = "CR"
    description = None


class DigitalRadiography(ProjectionRadiography):
    ontology_link = "http://www.radlex.org/RID/RID10351"
    dicom_modality = "DR"
    description = None


class DualEnergySubtractionRadiograpgy(ProjectionRadiography):
    ontology_link = "http://www.radlex.org/RID/RID10356"
    description = None


class Mammography(ProjectionRadiography):
    ontology_link = "http://www.radlex.org/RID/RID10357"
    description = None


class ScreenFilmRadiography(ProjectionRadiography):
    ontology_link = "http://www.radlex.org/RID/RID10353"
    description = "Conventional radiography"
    dicom_modality = "RG"


class Stereoscopy(ProjectionRadiography):
    ontology_link = "http://www.radlex.org/RID/RID50131"
    description = None


class StereotacticRadiography(ProjectionRadiography):
    ontology_link = "http://www.radlex.org/RID/RID50260"
    description = None


class Spectroscopy(ImagingModality):
    ontology_link = "http://www.radlex.org/RID/RID10377"
    description = (
        "The measurement of the amplitude of the components of a "
        "complex waveform throughout the frequency range of the "
        "waveform. (McGraw-Hill Dictionary of Scientific and "
        "Technical Terms, 4th ed) [MeSH]"
    )


class Tomography(ImagingModality):
    ontology_link = "http://www.radlex.org/RID/RID28840"
    description = None


class ComputedTomography(Tomography):
    ontology_link = "http://www.radlex.org/RID/RID10321"
    description = (
        "Tomography using x-ray transmission and a computer algorithm "
        "to reconstruct the image. [MeSH]"
    )
    dicom_modality = "CT"


class Ultrasound(ImagingModality):
    ontology_link = "http://www.radlex.org/RID/RID10326"
    description = (
        "The visualization of deep structures of the body by "
        "recording the reflections of echoes of pulses of ultrasonic "
        "waves directed into the tissues. Use of ultrasound for "
        "imaging or diagnostic purposes employs frequencies ranging "
        "from 1.6 to 10 megahertz. [MeSH]"
    )
    dicom_modality = "US"


# Some extra abbreviations
Mri = MagneticResonanceImaging
Pet = PositronEmissionTomography
Dmri = DiffusionMagneticResonanceImaging
Dti = DiffusionTensorImaging
Fmri = FunctionalMagneticResonanceImaging

# DICOM abbreviations, taken from: https://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_29.html
Cr = ComputedRadiography
Ct = ComputedTomography
Dx = DigitalRadiography
Mg = Mammography
Mr = MagneticResonanceImaging
Nm = NuclearMedicineImaging
Pt = PositronEmissionTomography
Px = PanographicRadiograph
Rf = RadioFluoroscopy
Rg = ScreenFilmRadiography
Us = Ultrasound
# AR = Autorefraction
# BI = Biomagnetic Imaging
# BMD = Bone Mineral Densitometry
# EPS = Cardiac Electrophysiology
# DMS = Dermoscopy
# DG = Diaphanography
# ECG = Electrocardiography
# EEG = Electroencephalography
# EMG = Electromyography
# EOG = Electrooculography
# ES = Endoscopy
# XC = External-camera Photography
# GM = General Microscopy
# HD = Hemodynamic Waveform
# IO = Intra-oral Radiography
# IVOCT = Intravascular Optical Coherence Tomography
# IVUS = Intravascular Ultrasound
# KER = Keratometry
# LS = Laser Scan
# LEN = Lensometry
# OAM = Ophthalmic Axial Measurements
# OPM = Ophthalmic Mapping
# OP = Ophthalmic Photography
# OPT = Ophthalmic Tomography
# OPTBSV = Ophthalmic Tomography B-scan Volume Analysis
# OPTENF = Ophthalmic Tomography En Face
# OPV = Ophthalmic Visual Field
# OCT = Optical Coherence Tomography
# OSS = Optical Surface Scanner
# PA = Photoacoustic
# POS = Position Sensor
# RESP = Respiratory Waveform
# RTIMAGE = RT Image
# SM = Slide Microscopy
# SRF = Subjective Refraction
# TG = Thermography
# BDUS = Ultrasound Bone Densitometry
# VA = Visual Acuity
# XA = X-Ray Angiography
