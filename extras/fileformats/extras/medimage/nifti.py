from pathlib import Path
import typing as ty
import nibabel
import numpy as np
from fileformats.core import FileSet, SampleFileGenerator
from fileformats.medimage import (
    MedicalImage,
    Nifti,
    NiftiGz,
    Nifti1,
    NiftiGzX,
    NiftiGzXBvec,
    NiftiXBvec,
    NiftiX,
    T1w,
    Fmri,
    Dmri,
    Brain,
)
import medimages4tests.dummy.nifti
import medimages4tests.mri.neuro.t1w
import medimages4tests.mri.neuro.dwi
import medimages4tests.mri.neuro.bold


@FileSet.read_metadata.register
def nifti_read_metadata(nifti: Nifti) -> ty.Mapping[str, ty.Any]:
    return dict(nibabel.load(nifti.fspath).header)


@MedicalImage.read_array.register
def nifti_data_array(nifti: Nifti) -> np.ndarray:  # noqa
    return nibabel.load(nifti.fspath).get_data()


@MedicalImage.vox_sizes.register
def nifti_vox_sizes(nifti: Nifti) -> ty.Tuple[float, float, float]:
    ndims = len(nifti_dims(nifti))
    return tuple(float(d) for d in nifti.metadata["pixdim"][1 : ndims + 1])


@MedicalImage.dims.register
def nifti_dims(nifti: Nifti) -> ty.Tuple[int, int, int]:
    dim_array = [int(d) for d in nifti.metadata["dim"]]
    for i in range(1, len(dim_array)):
        if all(d == 1 for d in dim_array[i:]):
            break  # Stop when the remaining dimensions are singletons
    return tuple(dim_array[1:i])


@FileSet.generate_sample_data.register
def nifti_generate_sample_data(
    nifti: Nifti1,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    return medimages4tests.dummy.nifti.get_image(
        out_file=generator.generate_fspath(file_type=Nifti1)
    )


@FileSet.generate_sample_data.register
def nifti_gz_generate_sample_data(
    nifti: NiftiGz,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    return medimages4tests.dummy.nifti.get_image(
        out_file=generator.generate_fspath(file_type=NiftiGz),
        compressed=True,
    )


@FileSet.generate_sample_data.register
def t1w_nifti_gz_x_generate_sample_data(
    nifti: NiftiGzX[T1w],
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    return _get_t1w_nifti_gz_x(generator)


@FileSet.generate_sample_data.register
def t1w_nifti_x_generate_sample_data(
    nifti: NiftiX[T1w],
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    nifti_gz_x = NiftiGzX(_get_t1w_nifti_gz_x(generator))
    return NiftiX.convert(nifti_gz_x)


@FileSet.generate_sample_data.register
def t1w_brain_nifti_gz_x_generate_sample_data(
    nifti: NiftiGzX[T1w, Brain],
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    return _get_t1w_nifti_gz_x(generator)


@FileSet.generate_sample_data.register
def t1w_brain_nifti_x_generate_sample_data(
    nifti: NiftiX[T1w, Brain],
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    nifti_gz_x = NiftiGzX(_get_t1w_nifti_gz_x(generator))
    return NiftiX.convert(nifti_gz_x)


@FileSet.generate_sample_data.register
def fmri_brain_nifti_gz_x_generate_sample_data(
    nifti: NiftiGzX[Fmri, Brain],
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    return _get_fmri_nifti_gz_x(generator)


@FileSet.generate_sample_data.register
def fmri_brain_nifti_x_generate_sample_data(
    nifti: NiftiX[Fmri, Brain],
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    nifti_gz_x = NiftiGzX(_get_fmri_nifti_gz_x(generator))
    return NiftiX.convert(nifti_gz_x)


@FileSet.generate_sample_data.register
def fmri_nifti_gz_x_generate_sample_data(
    nifti: NiftiGzX[Fmri],
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    return _get_fmri_nifti_gz_x(generator)


@FileSet.generate_sample_data.register
def fmri_nifti_x_generate_sample_data(
    nifti: NiftiX[Fmri],
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    nifti_gz_x = NiftiGzX(_get_fmri_nifti_gz_x(generator))
    return NiftiX.convert(nifti_gz_x)


@FileSet.generate_sample_data.register
def dmri_brain_nifti_gz_x_generate_sample_data(
    nifti: NiftiGzXBvec[Dmri, Brain],
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    return _get_dmri_nifti_gz_x(generator)


@FileSet.generate_sample_data.register
def dmri_brain_nifti_x_generate_sample_data(
    nifti: NiftiXBvec[Dmri, Brain],
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    nifti_gz_x = NiftiGzX(_get_dmri_nifti_gz_x(generator))
    return NiftiX.convert(nifti_gz_x)


@FileSet.generate_sample_data.register
def dmri_nifti_gz_x_generate_sample_data(
    nifti: NiftiGzXBvec[Dmri],
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    return _get_dmri_nifti_gz_x(generator)


@FileSet.generate_sample_data.register
def dmri_nifti_x_generate_sample_data(
    nifti: NiftiXBvec[Dmri],
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    nifti_gz_x = NiftiGzXBvec(_get_dmri_nifti_gz_x(generator))
    return NiftiX.convert(nifti_gz_x)


def _get_t1w_nifti_gz_x(generator: SampleFileGenerator) -> ty.Iterable[Path]:
    sample = generator.seed if generator.seed else "ds002014-01"
    fspaths = medimages4tests.mri.neuro.t1w.get_image(sample=sample)
    NiftiGzX(fspaths).copy(generator.dest_dir, mode=NiftiGzX.CopyMode.link_or_copy)
    return fspaths


def _get_fmri_nifti_gz_x(generator: SampleFileGenerator) -> ty.Iterable[Path]:
    sample = generator.seed if generator.seed else "ds002014-01"
    fspaths = medimages4tests.mri.neuro.bold.get_image(sample=sample)
    NiftiGzX(fspaths).copy(generator.dest_dir, mode=NiftiGzX.CopyMode.link_or_copy)
    return fspaths


def _get_dmri_nifti_gz_x(generator: SampleFileGenerator) -> ty.Iterable[Path]:
    sample = generator.seed if generator.seed else "ds004024-CON031"
    fspaths = medimages4tests.mri.neuro.dwi.get_image(sample=sample)
    NiftiGzX(fspaths).copy(generator.dest_dir, mode=NiftiGzX.CopyMode.link_or_copy)
    return fspaths
