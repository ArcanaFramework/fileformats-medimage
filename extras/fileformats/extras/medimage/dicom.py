from pathlib import Path
import typing as ty
from tempfile import mkdtemp
from random import Random
import pydicom
import numpy as np
from fileformats.core import FileSet
from fileformats.core.utils import gen_filename
from fileformats.medimage import MedicalImage, DicomCollection, DicomDir, DicomSeries
import medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c


@MedicalImage.read_array.register
def dicom_read_array(collection: DicomCollection):
    image_stack = []
    for dcm_file in collection.contents:
        image_stack.append(pydicom.dcmread(dcm_file).pixel_array)
    return np.asarray(image_stack)


@MedicalImage.vox_sizes.register
def dicom_vox_sizes(collection: DicomCollection):
    return tuple(
        collection.metadata["PixelSpacing"] + [collection.metadata["SliceThickness"]]
    )


@MedicalImage.dims.register
def dicom_dims(collection: DicomCollection):
    return tuple(
        (
            collection.metadata["Rows"],
            collection.metadata["DataColumns"],
            len(list(collection.contents)),
        ),
    )


@DicomCollection.series_number.register
def dicom_series_number(collection: DicomCollection):
    return str(collection.metadata["SeriesNumber"])


@FileSet.generate_sample_data.register
def dicom_dir_generate_sample_data(dcmdir: DicomDir, dest_dir: Path, seed: ty.Union[int, Random], stem: ty.Optional[str]):
    dcm_dir = medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c.get_image()
    # Set series number to random value to make it different
    if isinstance(seed, Random):
        rng = seed
    else:
        rng = Random(seed)
    series_number = rng.randint(1, SERIES_NUMBER_RANGE)
    dest = Path(dest_dir) / gen_filename(seed_or_rng=seed, stem=stem)
    dest.mkdir()
    for dcm_file in dcm_dir.iterdir():
        dcm = pydicom.dcmread(dcm_file)
        dcm.SeriesNumber = series_number
        pydicom.dcmwrite(dest / dcm_file.name, dcm)
    return [dest]


@FileSet.generate_sample_data.register
def dicom_set_generate_sample_data(dcm_series: DicomSeries, dest_dir: Path, seed: int, stem: ty.Optional[str]):
    rng = Random(seed)
    dicom_dir = dicom_dir_generate_sample_data(dcm_series, dest_dir=mkdtemp(), seed=rng, stem=None)[0]
    stem = gen_filename(rng, stem=stem)
    fspaths = []
    for i, dicom_file in enumerate(dicom_dir.iterdir(), start=1):
        fspaths.append(dicom_file.rename(dest_dir / f"{stem}-{i}.dcm"))
    return fspaths


SERIES_NUMBER_TAG = ("0020", "0011")
SERIES_NUMBER_RANGE = int(1e8)
