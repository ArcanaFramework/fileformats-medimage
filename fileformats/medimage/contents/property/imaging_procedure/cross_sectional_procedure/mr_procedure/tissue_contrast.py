from . import MrProcedure


class TissueContrast(MrProcedure):
    pass


class T1Weighted(TissueContrast):
    ontology_link = "http://www.radlex.org/RID/RID10794"
    description = "T1-weighted MRI image contrast"


class T2Weighted(TissueContrast):
    ontology_link = "http://www.radlex.org/RID/RID10795"
    description = "T2-weighted MRI image contrast"


class T2StarWeighted(TissueContrast):
    ontology_link = "http://www.radlex.org/RID/RID10796"
    description = "T2*-weighted MRI image contrast"


class T1T2Weighted(TissueContrast):
    ontology_link = "http://www.radlex.org/RID/RID10796"
    description = "T1/T2-weighted MRI image contrast"


class DiffusionWeighted(TissueContrast):
    ontology_link = "http://www.radlex.org/RID/RID10799"
    description = (
        "Assessment of the random Brownian motion of water molecules within the voxel."
    )


class FluidAttenuatedInversionRecovery(TissueContrast):
    ontology_link = "http://www.radlex.org/RID/RID35806"
    description = "Fluid Attenuated Inversion Recovery (FLAIR)"


class IntermediateWeighted(TissueContrast):
    ontology_link = "http://www.radlex.org/RID/RID10792"
    description = "Intermediate (proton density) weighted MRI image contrast"


Dwi = DiffusionWeighted
T1w = T1Weighted
T2w = T2Weighted
T2sw = T2StarWeighted
Flair = FluidAttenuatedInversionRecovery
T1T2w = T1T2Weighted

ProtonDensity = IntermediateWeighted
