from pathlib import Path
import typing as ty
from random import Random
import nibabel
import numpy as np
from fileformats.core import FileSet
from fileformats.core.utils import gen_filename
from fileformats.medimage import MedicalImage, Nifti, NiftiGz, Nifti1, NiftiGzX, NiftiX
import medimages4tests.dummy.nifti


@FileSet.read_metadata.register
def nifti_read_metadata(nifti: Nifti) -> ty.Mapping[str, ty.Any]:
    return dict(nibabel.load(nifti.fspath).header)


@MedicalImage.read_array.register
def nifti_data_array(nifti: Nifti) -> np.ndarray:  # noqa
    return nibabel.load(nifti.fspath).get_data()


@MedicalImage.vox_sizes.register
def nifti_vox_sizes(nifti: Nifti) -> ty.Tuple[float, float, float]:
    # FIXME: This won't work for 4-D files
    return tuple(float(d) for d in nifti.metadata["pixdim"][1:4])


@MedicalImage.dims.register
def nifti_dims(nifti: Nifti) -> ty.Tuple[int, int, int]:
    # FIXME: This won't work for 4-D files
    return tuple(int(d) for d in nifti.metadata["dim"][1:4])


@FileSet.generate_sample_data.register
def nifti_generate_sample_data(
    nifti: Nifti1, dest_dir: Path, seed: ty.Union[int, Random] = 0, stem: ty.Optional[str] = None
) -> ty.Iterable[Path]:
    return medimages4tests.dummy.nifti.get_image(
        out_file=dest_dir / gen_filename(seed, file_type=Nifti1, stem=stem)
    )


@FileSet.generate_sample_data.register
def nifti_gz_generate_sample_data(
    nifti: NiftiGz, dest_dir: Path, seed: ty.Union[int, Random] = 0, stem: ty.Optional[str] = None
) -> ty.Iterable[Path]:
    return medimages4tests.dummy.nifti.get_image(
        out_file=dest_dir / gen_filename(seed, file_type=NiftiGz, stem=stem),
        compressed=True,
    )


@FileSet.generate_sample_data.register
def nifti_gz_x_generate_sample_data(
    nifti: NiftiGzX, dest_dir: Path, seed: ty.Union[int, Random] = 0, stem: ty.Optional[str] = None
) -> ty.Iterable[Path]:
    return medimages4tests.mri.neuro.t1w.get_image()


@FileSet.generate_sample_data.register
def nifti_x_generate_sample_data(
    nifti: NiftiX, dest_dir: Path, seed: ty.Union[int, Random] = 0, stem: ty.Optional[str] = None
) -> ty.Iterable[Path]:
    nifti_gz_x = NiftiGzX(medimages4tests.mri.neuro.t1w.get_image())
    return NiftiX.convert(nifti_gz_x)
