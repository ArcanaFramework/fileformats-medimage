from pathlib import Path
import typing
import pydicom
import numpy
import numpy.typing
from fileformats.core import FileSet, extra_implementation
from fileformats.core import SampleFileGenerator
from fileformats.medimage import (
    MedicalImage,
    DicomCollection,
    DicomDir,
    DicomSeries,
)
from fileformats.medimage.base import DataArrayType
import medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c


@extra_implementation(MedicalImage.read_array)
def dicom_read_array(
    collection: DicomCollection,
) -> DataArrayType:
    image_stack = []
    for dcm_file in collection.contents:
        image_stack.append(pydicom.dcmread(dcm_file).pixel_array)
    return numpy.asarray(image_stack)


@extra_implementation(MedicalImage.vox_sizes)
def dicom_vox_sizes(collection: DicomCollection) -> typing.Tuple[float, float, float]:
    return tuple(
        collection.metadata["PixelSpacing"] + [collection.metadata["SliceThickness"]]
    )


@extra_implementation(MedicalImage.dims)
def dicom_dims(collection: DicomCollection) -> typing.Tuple[int, int, int]:
    return tuple(
        (
            collection.metadata["Rows"],
            collection.metadata["DataColumns"],
            len(list(collection.contents)),
        ),
    )


@extra_implementation(DicomCollection.series_number)
def dicom_series_number(collection: DicomCollection) -> str:
    return str(collection.metadata["SeriesNumber"])


@extra_implementation(FileSet.generate_sample_data)
def dicom_dir_generate_sample_data(
    dcmdir: DicomDir,
    generator: SampleFileGenerator,
) -> typing.List[Path]:
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
) -> typing.List[Path]:
    dicom_dir: Path = dicom_dir_generate_sample_data(dcm_series, generator=generator)[0]  # type: ignore[arg-type]
    stem = generator.generate_fspath().stem
    fspaths = []
    for i, dicom_file in enumerate(dicom_dir.iterdir(), start=1):
        fspaths.append(dicom_file.rename(generator.dest_dir / f"{stem}-{i}.dcm"))
    dicom_dir.rmdir()
    return fspaths


SERIES_NUMBER_TAG = ("0020", "0011")
SERIES_NUMBER_RANGE = int(1e8)
