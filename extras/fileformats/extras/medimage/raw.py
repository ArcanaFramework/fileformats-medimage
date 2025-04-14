import typing as ty
from pathlib import Path
import pydicom
import sys
from fileformats.core import SampleFileGenerator
from medimages4tests.dummy.raw.pet.siemens.biograph_vision.vr20b.pet_listmode import (
    get_data as get_pet_listmode_data,
)
from medimages4tests.dummy.raw.pet.siemens.biograph_vision.vr20b.pet_countrate import (
    get_data as get_pet_countrate_data,
)
from fileformats.core import extra_implementation, FileSet
from fileformats.medimage.dicom import DicomImage
from fileformats.medimage.raw import (
    Vnd_Siemens_Biograph128Vision_Vr20b_LargePetRawData,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetCountRate,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetListMode,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetCtRawData,
)
from fileformats.core.io import BinaryIOWindow

if sys.version_info >= (3, 9):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

TagListType: TypeAlias = ty.Union[
    ty.List[int],
    ty.List[str],
    ty.List[ty.Tuple[int, int]],
    ty.List[pydicom.tag.BaseTag],
]


@extra_implementation(FileSet.read_metadata)
def siemens_pet_raw_data_read_metadata(
    pet_raw_data: Vnd_Siemens_Biograph128Vision_Vr20b_LargePetRawData,
    specific_tags: ty.Optional[TagListType] = None,
    **kwargs: ty.Any,
) -> ty.Mapping[str, ty.Any]:

    with pet_raw_data.open() as f:
        window = BinaryIOWindow(
            f,  # type: ignore[arg-type]
            pet_raw_data.dicom_header_offset,
            pet_raw_data.dcm_hdr_size_int_offset,
        )
        dcm = pydicom.dcmread(window, specific_tags=specific_tags)
    return DicomImage.pydicom_to_dict(dcm)


@extra_implementation(FileSet.read_metadata)
def siemens_petct_raw_data_read_metadata(
    pet_raw_data: Vnd_Siemens_Biograph128Vision_Vr20b_PetCtRawData,
    specific_tags: ty.Optional[TagListType] = None,
    **kwargs: ty.Any,
) -> ty.Mapping[str, ty.Any]:

    with pet_raw_data.open() as f:
        window = BinaryIOWindow(
            f,  # type: ignore[arg-type]
            *pet_raw_data.dicom_header_limits,
        )
        dcm = pydicom.dcmread(window, specific_tags=specific_tags)
    return DicomImage.pydicom_to_dict(dcm)


@extra_implementation(FileSet.generate_sample_data)
def siemens_pet_listmode_generate_sample_data(
    pet_raw_data: Vnd_Siemens_Biograph128Vision_Vr20b_PetListMode,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    return get_pet_listmode_data(out_dir=generator.dest_dir)  # type: ignore[no-any-return]


@extra_implementation(FileSet.generate_sample_data)
def siemens_pet_countrate_generate_sample_data(
    pet_raw_data: Vnd_Siemens_Biograph128Vision_Vr20b_PetCountRate,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    return get_pet_countrate_data(out_dir=generator.dest_dir)  # type: ignore[no-any-return]
