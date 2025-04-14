import sys
import os
import typing as ty
from collections import defaultdict, Counter
from pathlib import Path
from fileformats.core.decorators import mtime_cached_property
from fileformats.core import extra, FileSet, extra_implementation
from fileformats.core.collection import TypedCollection
from fileformats.generic import TypedDirectory, TypedSet
from fileformats.application import Dicom
from .base import MedicalImage

if sys.version_info >= (3, 9):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if ty.TYPE_CHECKING:
    import pydicom.tag

    TagListType: TypeAlias = ty.Union[
        ty.List[int],
        ty.List[str],
        ty.List[ty.Tuple[int, int]],
        ty.List[pydicom.tag.BaseTag],
    ]
# =====================================================================
# Custom loader functions for different image types
# =====================================================================


class DicomImage(MedicalImage, Dicom):
    """A DICOM file that contains image data. Derives from the generic Dicom class in
    the `application` namespace as well as medical image base class"""


def dicom_sort_key(dicom: Dicom) -> str:
    """Sorts DICOM objects by SOPInstanceUID"""
    assert isinstance(dicom.metadata, dict)
    return dicom.metadata["SOPInstanceUID"]  # type: ignore[no-any-return]


class DicomCollection(MedicalImage, TypedCollection):
    """Base class for collections of DICOM files, which can either be stored within a
    directory (DicomDir) or presented as a flat list (DicomSeries)
    """

    content_types = (DicomImage,)

    def __len__(self) -> int:
        return len(self.contents)

    @extra
    def series_number(self) -> str:
        raise NotImplementedError


class DicomDir(TypedDirectory, DicomCollection):
    content_types = (DicomImage,)

    @mtime_cached_property
    def contents(self) -> ty.List[DicomImage]:
        return sorted(TypedDirectory.contents.__get__(self), key=dicom_sort_key)


class DicomSeries(TypedSet, DicomCollection):
    content_types = (DicomImage,)

    @classmethod
    def from_paths(
        cls,
        fspaths: ty.Iterable[Path],
        common_ok: bool = False,
        **kwargs: ty.Any,
    ) -> ty.Tuple[ty.Set[Self], ty.Set[Path]]:
        """Separates a list of DICOM files into separate series from the file-system
        paths

        Parameters
        ----------
        fspaths : ty.Iterable[Path]
            the fspaths pointing to the DICOM files
        common_ok : bool, optional
            included to match the signature of the overridden method, but ignored as each
            dicom should belong to only one series.
        specific_tags : ty.Optional[TagListType], optional
            the DICOM tags to read from the files. If None, the default tags will be
            read
        **kwargs : ty.Any
            additional keyword arguments to passed through to the DicomImage constructor

        Returns
        -------
        tuple[set[DicomSeries], set[Path]]
            the found dicom series objects and any unrecognised file paths
        """
        dicoms, remaining = DicomImage.from_paths(
            fspaths, common_ok=common_ok, **kwargs
        )
        series_dict = defaultdict(list)
        for dicom in dicoms:
            metadata = dicom.read_metadata(specific_tags=cls.ID_KEYS)
            series_dict[tuple(metadata[k] for k in cls.ID_KEYS)].append(dicom)
        return set([cls(d.fspath for d in s) for s in series_dict.values()]), remaining

    @mtime_cached_property
    def contents(self) -> ty.List[DicomImage]:
        return sorted(TypedSet.contents.__get__(self), key=dicom_sort_key)

    ID_KEYS = ("StudyInstanceUID", "SeriesNumber")


@extra_implementation(FileSet.read_metadata)
def dicom_collection_read_metadata(
    collection: DicomCollection, **kwargs: ty.Any
) -> ty.Mapping[str, ty.Any]:
    # Collated DICOM headers across series
    collated: ty.Dict[str, ty.Any] = {}
    key_repeats: ty.Counter[str] = Counter()
    varying_keys = set()
    # We use the "contents" property implementation in TypeSet instead of the overload
    # in DicomCollection because we don't want the metadata to be read ahead of the
    # the `select_metadata` call below
    base_class: ty.Union[ty.Type[TypedSet], ty.Type[TypedDirectory]] = (
        TypedSet if isinstance(collection, DicomSeries) else TypedDirectory
    )
    for dicom in base_class.contents.__get__(collection):
        for key, val in dicom.metadata.items():
            try:
                prev_val = collated[key]
            except KeyError:
                collated[
                    key
                ] = val  # Insert initial value (should only happen on first iter)
                key_repeats.update([key])
            else:
                if key in varying_keys:
                    collated[key].append(val)
                # Check whether the value is the same as the values in the previous
                # images in the series
                elif val != prev_val:
                    collated[key] = [prev_val] * key_repeats[key] + [val]
                    varying_keys.add(key)
                else:
                    key_repeats.update([key])
    return collated


def get_dicom_tag(
    file: ty.Union[str, os.PathLike[ty.Any], ty.BinaryIO],
    target_tag: ty.Tuple[int, int],
) -> ty.Union[str, bytes, None]:
    """A basic function to read a DICOM file and extract the value of a specific tag.
    This is a low-level function that does not use any external libraries.
    It is not a replacement for pydicom, but can be used to extract specific tags
    without loading the entire DICOM file into memory.

    Parameters
    ----------
    filepath : str or os.PathLike
        The path to the DICOM file.
    target_tag : tuple[int, int]
        The DICOM tag to extract, specified as a tuple of (group, element).
        For example, (0x0010, 0x0010) for PatientName.

    Returns
    -------
    str or bytes or None
        The value of the specified DICOM tag, decoded as a string if possible.
        If the tag is not found or cannot be decoded, returns None.
    """
    if isinstance(file, (str, os.PathLike)):
        filepath = file
        file_stream = open(filepath, "rb")
        close_stream = True
    elif hasattr(file, "read"):
        file_stream = file  # type: ignore[assignment]
        close_stream = False
    else:
        raise TypeError("file must be a path-like object or a binary stream")

    try:
        file_stream.seek(132)  # Skip preamble and 'DICM' if at file start

        while True:
            tag_bytes = file_stream.read(4)
            if len(tag_bytes) < 4:
                break

            group = int.from_bytes(tag_bytes[:2], "little")
            element = int.from_bytes(tag_bytes[2:], "little")
            tag = (group, element)

            vr = file_stream.read(2).decode()

            if vr in {"OB", "OW", "OF", "SQ", "UT", "UN"}:
                file_stream.read(2)  # reserved
                length = int.from_bytes(file_stream.read(4), "little")
            else:
                length = int.from_bytes(file_stream.read(2), "little")

            value = file_stream.read(length)

            if tag == target_tag:
                try:
                    return value.decode().strip()
                except UnicodeDecodeError:
                    return value
    finally:
        if close_stream:
            file_stream.close()

    return None  # Not found


# class Vnd_Siemens_Vision(DicomImage):
#     ext = ".ima"


# class Vnd_Siemens_VisionDir(DicomDir):
#     content_types = (Vnd_Siemens_Vision,)
