from pathlib import Path
from fileformats.medimage.raw import Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData

ptd = Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData(
    Path(
        "~/Data/tbp/0007_001_2408131530/605-605-EM_SINO/"
        "MANGO_P001_FMISO_PresurgeryDynamic.PT.PET_U_TBPC230007_MANGO_First_(Adult)."
        "605.PET_EM_SINO.2024.08.13.18.54.47.656000.2.0.602877000.ptd"
    ).expanduser()
)

print(ptd.metadata["AcquisitionTime"])
