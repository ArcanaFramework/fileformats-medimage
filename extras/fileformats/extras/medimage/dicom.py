from pathlib import Path
import typing as ty
import pydicom
import numpy as np
from fileformats.core import FileSet
from fileformats.core import SampleFileGenerator
from fileformats.medimage import MedicalImage, DicomCollection, DicomDir, DicomSeries
import medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c


@MedicalImage.read_array.register
def dicom_read_array(collection: DicomCollection) -> np.ndarray:
    image_stack = []
    for dcm_file in collection.contents:
        image_stack.append(pydicom.dcmread(dcm_file).pixel_array)
    return np.asarray(image_stack)


@MedicalImage.vox_sizes.register
def dicom_vox_sizes(collection: DicomCollection) -> ty.Tuple[float, float, float]:
    return tuple(
        collection.metadata["PixelSpacing"] + [collection.metadata["SliceThickness"]]
    )


@MedicalImage.dims.register
def dicom_dims(collection: DicomCollection) -> ty.Tuple[int, int, int]:
    return tuple(
        (
            collection.metadata["Rows"],
            collection.metadata["DataColumns"],
            len(list(collection.contents)),
        ),
    )


@DicomCollection.series_number.register
def dicom_series_number(collection: DicomCollection) -> str:
    return str(collection.metadata["SeriesNumber"])


@FileSet.generate_sample_data.register
def dicom_dir_generate_sample_data(
    dcmdir: DicomDir,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    dcm_dir = medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c.get_image()
    series_number = generator.rng.randint(1, SERIES_NUMBER_RANGE)
    dest = generator.generate_fspath(DicomDir)
    dest.mkdir()
    for dcm_file in dcm_dir.iterdir():
        dcm = pydicom.dcmread(dcm_file)
        dcm.SeriesNumber = series_number
        pydicom.dcmwrite(dest / dcm_file.name, dcm)
    return [dest]


@FileSet.generate_sample_data.register
def dicom_series_generate_sample_data(
    dcm_series: DicomSeries,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    dicom_dir: Path = dicom_dir_generate_sample_data(dcm_series, generator=generator)[0]
    stem = generator.generate_fspath().stem
    fspaths = []
    for i, dicom_file in enumerate(dicom_dir.iterdir(), start=1):
        fspaths.append(dicom_file.rename(generator.dest_dir / f"{stem}-{i}.dcm"))
    dicom_dir.rmdir()
    return fspaths


SERIES_NUMBER_TAG = ("0020", "0011")
SERIES_NUMBER_RANGE = int(1e8)
