import typing as ty
import pydicom
from fileformats.core import extra_implementation, FileSet
from fileformats.medimage.raw import Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData


@extra_implementation(FileSet.read_metadata)
def siemens_pet_raw_data_read_metadata(
    pet_raw_data: Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData,
) -> ty.Mapping[str, ty.Any]:
    with pet_raw_data.open() as f:
        assert isinstance(f, ty.BinaryIO)
        dcm = pydicom.dcmread(f)
    return dcm  # type: ignore[return-value]
