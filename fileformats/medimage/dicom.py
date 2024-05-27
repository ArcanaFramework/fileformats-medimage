import typing as ty
from collections import defaultdict, Counter
from pathlib import Path
from functools import cached_property
from fileformats.core import hook, FileSet
from fileformats.generic import DirectoryContaining, SetOf, TypedSet
from fileformats.application import Dicom
from .base import MedicalImage

# =====================================================================
# Custom loader functions for different image types
# =====================================================================


def dicom_sort_key(dicom: Dicom) -> str:
    """Sorts DICOM objects by SOPInstanceUID"""
    return dicom.metadata["SOPInstanceUID"]


class DicomCollection(MedicalImage):
    """Base class for collections of DICOM files, which can either be stored within a
    directory (DicomDir) or presented as a flat list (DicomSeries)
    """

    content_types = (Dicom,)
    iana_mime = None

    def __len__(self):
        return len(self.contents)

    @hook.extra
    def series_number(self) -> str:
        raise NotImplementedError


class DicomDir(DicomCollection, DirectoryContaining[Dicom]):

    @cached_property
    def contents(self) -> ty.List[Dicom]:
        return sorted(super().contents, key=dicom_sort_key)


class DicomSeries(DicomCollection, SetOf[Dicom]):
    @classmethod
    def from_paths(
        cls,
        fspaths: ty.Iterable[Path],
        common_ok: bool = False,
        selected_keys: ty.Optional[ty.Sequence[str]] = None,
    ) -> ty.Tuple[ty.Set["DicomSeries"], ty.Set[Path]]:
        """Separates a list of DICOM files into separate series from the file-system
        paths

        Parameters
        ----------
        fspaths : ty.Iterable[Path]
            the fspaths pointing to the DICOM files
        common_ok : bool, optional
            included to match the signature of the overriden method, but ignored as each
            dicom should belong to only one series.
        selected_keys : ty.Optional[ty.Sequence[str]], optional
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
            dicom.select_metadata(selected_keys)
            series_dict[
                (
                    str(dicom.metadata["StudyInstanceUID"]),
                    str(dicom.metadata["SeriesNumber"]),
                )
            ].append(dicom)
        return set([cls(s) for s in series_dict.values()]), remaining

    @cached_property
    def contents(self) -> ty.List[Dicom]:
        return sorted(super().contents, key=dicom_sort_key)


@FileSet.read_metadata.register
def dicom_collection_read_metadata(
    collection: DicomCollection, selected_keys: ty.Optional[ty.Sequence[str]] = None
) -> ty.Mapping[str, ty.Any]:
    # Collated DICOM headers across series
    collated = {}
    key_repeats = Counter()
    varying_keys = set()
    # We use the "contents" property implementation in TypeSet instead of the overload
    # in DicomCollection because we don't want the metadata to be read ahead of the
    # the `select_metadata` call below
    base_class = (
        TypedSet if isinstance(collection, DicomSeries) else DirectoryContaining
    )
    for dicom in base_class.contents.fget(collection):
        dicom.select_metadata(selected_keys)
        for key, val in dicom.metadata.items():
            try:
                prev_val = collated[key]
            except KeyError:
                collated[key] = (
                    val  # Insert initial value (should only happen on first iter)
                )
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
