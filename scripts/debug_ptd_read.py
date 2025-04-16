from pathlib import Path
from fileformats.core import from_paths

# from fileformats.medimage.raw import Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData
from fileformats.medimage.raw import (
    Vnd_Siemens_Biograph128Vision_Vr20b_PetDynamicSinogramSeries,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetParameterisation,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetSinogram,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetNormalisation,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetCountRate,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetListMode,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetCtSpl,
)

Vnd_Siemens_Biograph128Vision_Vr20b_PetCtSpl(
    "/Users/tclose/Data/tbp/PET_Raw_Data_0602/PHYSICS_SUV_TEST_PVE_F18.PT.PET_Onco_(Adult).602.PETCT_SPL.2023.07.27.08.49.11.676000.2.0.2761828.ptd"
)

filesets = from_paths(
    Path("/Users/tclose/Data/tbp/").glob("**/*.ptd"),
    Vnd_Siemens_Biograph128Vision_Vr20b_PetDynamicSinogramSeries,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetParameterisation,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetSinogram,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetNormalisation,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetCountRate,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetListMode,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetCtSpl,
)


# ptd = Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData(
#     Path(
#         "/Users/tclose/Data/tbp/PET_Raw_Data_0602/"
#         "PHYSICS_SUV_TEST_PVE_F18.PT.PET_Onco_(Adult).602.PET_LISTMODE.2023.07.27.08.49.11.676000.2.0.2761856.ptd"
#     ).expanduser()
# )

# mdata = ptd.metadata

assert filesets
