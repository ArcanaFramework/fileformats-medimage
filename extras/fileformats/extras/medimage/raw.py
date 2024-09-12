import typing as ty
import pydicom
from fileformats.core import extra_implementation, FileSet
from fileformats.medimage.raw import Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData
from fileformats.core.io import BinaryIOWindow


@extra_implementation(FileSet.read_metadata)
def siemens_pet_raw_data_read_metadata(
    pet_raw_data: Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData,
    selected_keys: ty.Optional[ty.Collection[str]] = None,
) -> ty.Mapping[str, ty.Any]:

    with pet_raw_data.open() as f:
        window = BinaryIOWindow(
            f,  # type: ignore[arg-type]
            pet_raw_data.dicom_header_offset,
            pet_raw_data.dcm_hdr_size_int_offset,
        )
        if selected_keys is not None:
            selected_keys = list(selected_keys)
        dcm = pydicom.dcmread(window, specific_tags=selected_keys)
    return dcm  # type: ignore[return-value]
