from pathlib import Path
from fileformats.medimage.raw import Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData

ptd = Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData(
    Path(
        "/Users/tclose/Data/tbp/PET_Raw_Data_0602/"
        "PHYSICS_SUV_TEST_PVE_F18.PT.PET_Onco_(Adult).602.PET_LISTMODE.2023.07.27.08.49.11.676000.2.0.2761856.ptd"
    ).expanduser()
)

mdata = ptd.metadata

assert mdata
