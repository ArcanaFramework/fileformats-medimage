import logging
import os
import typing as ty
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import fileformats.extras.application.medical  # noqa: F401
import medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c
import numpy
import numpy.typing
import pydicom
from deid.config import DeidRecipe
from deid.dicom.parser import DicomParser
from fileformats.core import FileSet, SampleFileGenerator, extra_implementation

from fileformats.medimage import (
    DicomCollection,
    DicomDir,
    DicomImage,
    DicomSeries,
    MedicalImage,
    MedicalImagingData,
)
from fileformats.medimage.base import DataArrayType

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Variable builders for deid spec var: references
# ---------------------------------------------------------------------------
# Each callable receives the pydicom Dataset and returns the substitution
# value. Sites can override any entry by passing variable_builders={...}
# to dicom_deidentify.
# ---------------------------------------------------------------------------

VariableBuilder = ty.Callable[[pydicom.Dataset], str | int]

DEFAULT_RECIPE = Path(__file__).parent / "recipe.dicom"

DEFAULT_VARIABLE_BUILDERS: dict[str, VariableBuilder] = {
    "anon_birth_date": lambda ds: str(ds.get("PatientBirthDate", ""))[:4] + "0101",
    "anon_patient_name": lambda ds: str(ds.get("PatientID", "")),
    "anon_patient_id": lambda ds: (
        f"{ds.get('PatientID', '')}-{ds.get('AcquisitionTime', '')}"
    ),
    "patient_comments": lambda ds: (
        f"Project={ds.get('ReferringPhysicianName', '')};"
        f"Subject={ds.get('PatientID', '')};"
        f"Session={ds.get('PatientID', '')}-{ds.get('AcquisitionTime', '')}"
    ),
    "date_jitter": lambda _ds: int(os.environ.get("DEID_DATE_JITTER", "0")),
}


@extra_implementation(MedicalImage.read_array)
def dicom_read_array(
    collection: DicomCollection,
) -> DataArrayType:
    image_stack = []
    for dcm_file in collection.contents:
        image_stack.append(pydicom.dcmread(dcm_file).pixel_array)
    return numpy.asarray(image_stack)


@extra_implementation(MedicalImage.vox_sizes)
def dicom_vox_sizes(collection: DicomCollection) -> tuple[float, float, float]:
    return tuple(
        collection.metadata["PixelSpacing"] + [collection.metadata["SliceThickness"]]
    )


@extra_implementation(MedicalImage.dims)
def dicom_dims(collection: DicomCollection) -> tuple[int, int, int]:
    return (
        collection.metadata["Rows"],
        collection.metadata["DataColumns"],
        len(list(collection.contents)),
    )


@extra_implementation(DicomCollection.series_number)
def dicom_series_number(collection: DicomCollection) -> str:
    return str(collection.metadata["SeriesNumber"])


@extra_implementation(FileSet.generate_sample_data)
def dicom_dir_generate_sample_data(
    dcmdir: DicomDir,
    generator: SampleFileGenerator,
) -> list[Path]:
    dcm_dir = medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c.get_image()
    series_number = generator.rng.randint(1, SERIES_NUMBER_RANGE)
    dest = generator.generate_fspath(DicomDir)
    dest.mkdir()
    for dcm_file in dcm_dir.iterdir():
        dcm = pydicom.dcmread(dcm_file)
        dcm.SeriesNumber = series_number
        pydicom.dcmwrite(dest / dcm_file.name, dcm)
    return [dest]


@extra_implementation(FileSet.generate_sample_data)
def dicom_series_generate_sample_data(
    dcm_series: DicomSeries,
    generator: SampleFileGenerator,
) -> list[Path]:
    dicom_dir: Path = dicom_dir_generate_sample_data(dcm_series, generator=generator)[0]  # type: ignore[arg-type]
    stem = generator.generate_fspath().stem
    fspaths = []
    for i, dicom_file in enumerate(dicom_dir.iterdir(), start=1):
        fspaths.append(dicom_file.rename(generator.dest_dir / f"{stem}-{i}.dcm"))
    dicom_dir.rmdir()
    return fspaths


SERIES_NUMBER_TAG = ("0020", "0011")
SERIES_NUMBER_RANGE = int(1e8)


@extra_implementation(MedicalImagingData.deidentify)
def dicom_deidentify(
    dicom: DicomImage,
    out_dir: os.PathLike[str],
    spec: str | Path | None = None,
    **kwargs: ty.Any,
) -> DicomImage:
    variable_builders: dict[str, VariableBuilder] | None = kwargs.pop(
        "variable_builders", None
    )
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    outfile = out_dir / dicom.fspath.name

    spec_path = spec if spec is not None else DEFAULT_RECIPE
    deid_spec = DeidRecipe(str(spec_path))

    parser = DicomParser(str(dicom.fspath), recipe=deid_spec)

    builders = {**DEFAULT_VARIABLE_BUILDERS, **(variable_builders or {})}
    ds = parser.dicom
    for var_name, builder in builders.items():
        try:
            value = builder(ds)
            parser.define(var_name, value)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Variable builder for '%s' raised %s: %s — skipping",
                var_name, type(exc).__name__, exc,
            )

    parser.parse(strip_sequences=True, remove_private=True)
    parser.save(str(outfile))

    return type(dicom)(outfile)


@extra_implementation(MedicalImagingData.deidentify)
def dicom_collection_deidentify(
    collection: DicomCollection,
    out_dir: os.PathLike[str],
    spec: str | Path | None = None,
    **kwargs: ty.Any,
) -> DicomCollection:
    variable_builders: dict[str, VariableBuilder] | None = kwargs.pop(
        "variable_builders", None
    )
    max_workers: int | None = kwargs.pop("max_workers", None)
    out_dir = Path(out_dir)
    if isinstance(collection, DicomDir):
        out_dir /= collection.name
    out_dir.mkdir(parents=True, exist_ok=True)

    def _deidentify_one(dicom: DicomImage) -> Path:
        return dicom.deidentify(
            out_dir, spec=spec, variable_builders=variable_builders
        ).fspath

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        deid_fspaths = list(executor.map(_deidentify_one, collection.contents))
    type_ = type(collection)
    if isinstance(collection, DicomDir):
        deidentified = type_(Path(out_dir))
    else:
        deidentified = type_(deid_fspaths)
    return deidentified
