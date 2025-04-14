import io
import typing as ty
from fileformats.generic import TypedSet
from fileformats.core import mtime_cached_property, validated_property
from fileformats.core.exceptions import FormatMismatchError
from fileformats.core.mixin import WithMagicNumber
from fileformats.medimage.dicom import get_dicom_tag
from fileformats.core.io import BinaryIOWindow
from .base import (
    PetRawData,
    PetListMode,
    PetSinogram,
    PetCountRate,
    PetNormalisation,
)


class Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData(WithMagicNumber, PetRawData):
    """PET raw data format as produced by Siemens Biograph 128 Vision. It is used to
    store a range of raw PET data such as list-mode, calibration and sinogram files.

    Consists of a block of raw data, followed by a DICOM header, an int4 containing
    the size of the DICOM header, and then the number b'LARGE_PET_LM_RAWDATA'.
    """

    ext = ".ptd"
    magic_number = b"LARGE_PET_LM_RAWDATA"
    magic_number_offset = -len(magic_number)  # magic number is at end of file
    expected_image_type: str = ""  # For sub-classes to specify the expected image tag
    IMAGE_TYPE_TAG = (0x0008, 0x0008)

    # Size in bytes of the integer that defines the size of the dicom header
    sizeof_dcm_hdr_size_int: int = 4
    # Offset from the end of the file where the magic number and header size integer
    dcm_hdr_size_int_offset: int = magic_number_offset - sizeof_dcm_hdr_size_int

    @mtime_cached_property
    def dicom_header_size(self) -> int:
        with self.open() as f:
            f.seek(self.dcm_hdr_size_int_offset, io.SEEK_END)
            dcm_hdr_size_bytes: bytes = f.read(self.sizeof_dcm_hdr_size_int)
            return int.from_bytes(dcm_hdr_size_bytes, "little")

    @validated_property
    def dicom_header_offset(self) -> int:
        dcm_hdr_size: int = self.dicom_header_size
        return -dcm_hdr_size + self.dcm_hdr_size_int_offset

    def read_tag(self, tag: ty.Tuple[int, int]) -> ty.Union[str, bytes, None]:
        with self.open() as f:
            window = BinaryIOWindow(
                f,  # type: ignore[arg-type]
                self.dicom_header_offset,
                self.dcm_hdr_size_int_offset,
            )
            value = get_dicom_tag(window, tag)
        return value

    @validated_property
    def image_type(self) -> str:
        image_type_seq: ty.List[str] = self._image_type_seq
        if self.expected_image_type:
            if (
                not isinstance(image_type_seq, list)
                or len(image_type_seq) != 3
                or image_type_seq[:2] != ["ORIGINAL", "PRIMARY"]
            ):
                raise FormatMismatchError(
                    f"Image type of {self} ({image_type_seq!r}) does not match expected "
                    f"form ['ORIGINAL', 'PRIMARY', *]"
                )
            image_type = image_type_seq[2]
            if self.expected_image_type != image_type:
                raise FormatMismatchError(
                    f"Image type of {self} ({image_type!r}) does not match expected "
                    f"({self.expected_image_type!r})"
                )
        return image_type

    @mtime_cached_property
    def _image_type_seq(self) -> ty.List[str]:
        value = self.read_tag(self.IMAGE_TYPE_TAG)
        assert isinstance(value, str)
        return value.split("\\")


class Vnd_Siemens_Biograph128Vision_Vr20b_PetListMode(
    Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData, PetListMode
):
    expected_image_type = "PET_LISTMODE"


class Vnd_Siemens_Biograph128Vision_Vr20b_PetSinogram(
    Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData, PetSinogram
):
    "histogrammed projection data in a reconstruction-friendly format"

    expected_image_type = "PET_EM_SINO"


class Vnd_Siemens_Biograph128Vision_Vr20b_PetCountRate(
    Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData, PetCountRate
):
    "number of prompt/random/single events per unit time"

    expected_image_type = "PET_COUNTRATE"


class Vnd_Siemens_Biograph128Vision_Vr20b_PetNormalisation(
    Vnd_Siemens_Biograph128Vision_Vr20b_PetRawData, PetNormalisation
):
    "normalisation scan or the current cross calibration factor"

    expected_image_type = "PET_NORM"


class Vnd_Siemens_Biograph128Vision_Vr20b_PetSinogramSeries(TypedSet):
    "Series of sinogram images"

    content_types = (Vnd_Siemens_Biograph128Vision_Vr20b_PetSinogram,)
