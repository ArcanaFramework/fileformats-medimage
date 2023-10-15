import typing as ty
from copy import copy
from operator import itemgetter
from collections import defaultdict
from pathlib import Path
from functools import cached_property
from fileformats.core import mark, FileSet
from fileformats.generic import DirectoryContaining, SetOf
from fileformats.application import Dicom
from .base import MedicalImage

# =====================================================================
# Custom loader functions for different image types
# =====================================================================


class DicomCollection(MedicalImage):
    """Base class for collections of DICOM files, which can either be stored within a
    directory (DicomDir) or presented as a flat list (DicomSeries)
    """

    content_types = (Dicom,)
    iana_mime = None

    def __len__(self):
        return len(self.contents)

    @mark.extra
    def series_number(self):
        raise NotImplementedError

    @cached_property
    def contents(self) -> ty.List[Dicom]:
        return sorted(super().contents, key=itemgetter("SOPInstanceUID"))


class DicomDir(DicomCollection, DirectoryContaining[Dicom]):
    pass


class DicomSeries(DicomCollection, SetOf[Dicom]):

    @classmethod
    def from_paths(
        cls, fspaths: ty.Iterable[Path], common_ok: bool = False
    ) -> ty.Tuple[ty.Set[FileSet], ty.Set[Path]]:
        dicoms, remaining = Dicom.from_paths(fspaths, common_ok=common_ok)
        series_dict = defaultdict(list)
        for dicom in dicoms:
            series_dict[dicom["SeriesNumber"]].append(dicom)
        return set([cls(s) for s in series_dict.values()]), remaining


@FileSet.read_metadata.register
def dicom_collection_read_metadata(collection: DicomCollection) -> ty.Dict[str, ty.Any]:
    # Collated DICOM headers across series
    collated = copy(collection.contents[0].metadata)
    if len(collection.contents) > 1:
        for key, val in collection.contents[1].metadata.items():
            if val != collated[key]:  # Turn field into list
                collated[key] = [collated[key], val]
    for dicom in collection.contents[2:]:
        for key, val in dicom.metadata.items():
            if val != collated[key]:
                collated[key].append(val)
    return collated
