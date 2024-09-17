import typing as ty
from collections import defaultdict, Counter
from pathlib import Path
from abc import ABCMeta, abstractproperty
from fileformats.core.decorators import mtime_cached_property
from fileformats.core import extra, FileSet, extra_implementation
from fileformats.generic import Directory, TypedSet
from fileformats.application import Dicom
from .base import MedicalImage

# =====================================================================
# Custom loader functions for different image types
# =====================================================================


def dicom_sort_key(dicom: Dicom) -> str:
    """Sorts DICOM objects by SOPInstanceUID"""
    assert isinstance(dicom.metadata, dict)
    return dicom.metadata["SOPInstanceUID"]  # type: ignore[no-any-return]


class DicomCollection(MedicalImage, metaclass=ABCMeta):
    """Base class for collections of DICOM files, which can either be stored within a
    directory (DicomDir) or presented as a flat list (DicomSeries)
    """

    content_types: ty.Tuple[ty.Type[FileSet], ...] = (Dicom,)

    def __len__(self) -> int:
        return len(self.contents)

    @extra
    def series_number(self) -> str:
        raise NotImplementedError

    @abstractproperty
    def contents(self) -> ty.List[Dicom]:
        raise NotImplementedError


class DicomDir(DicomCollection, Directory):

    content_types = (Dicom,)

    @mtime_cached_property
    def contents(self) -> ty.List[Dicom]:  # type: ignore[override]
        return sorted(Directory.contents.__get__(self), key=dicom_sort_key)


class DicomSeries(DicomCollection, TypedSet):
    @classmethod
    def from_paths(
        cls,
        fspaths: ty.Iterable[Path],
        common_ok: bool = False,
    ) -> ty.Tuple[ty.Set["DicomSeries"], ty.Set[Path]]:
        """Separates a list of DICOM files into separate series from the file-system
        paths

        Parameters
        ----------
        fspaths : ty.Iterable[Path]
            the fspaths pointing to the DICOM files
        common_ok : bool, optional
            included to match the signature of the overridden method, but ignored as each
            dicom should belong to only one series.
        selected_keys : ty.Optional[ty.Collection[str]], optional
            metadata keys to load from the DICOM files, typically used for performance
            reasons, by default None (i.e. all metadata is loaded)

        Returns
        -------
        tuple[set[DicomSeries], set[Path]]
            the found dicom series objects and any unrecognised file paths
        """
        dicoms, remaining = Dicom.from_paths(fspaths, common_ok=common_ok)
        series_dict = defaultdict(list)
        for dicom in dicoms:
            metadata = dicom.read_metadata(selected_keys=cls.ID_KEYS)
            series_dict[tuple(metadata[k] for k in cls.ID_KEYS)].append(dicom)
        return set([cls(d.fspath for d in s) for s in series_dict.values()]), remaining

    @mtime_cached_property
    def contents(self) -> ty.List[Dicom]:  # type: ignore[override]
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
    base_class: ty.Union[ty.Type[TypedSet], ty.Type[Directory]] = (
        TypedSet if isinstance(collection, DicomSeries) else Directory
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


# class Vnd_Siemens_Vision(Dicom):
#     ext = ".ima"


# class Vnd_Siemens_VisionDir(DicomDir):
#     content_types = (Vnd_Siemens_Vision,)
