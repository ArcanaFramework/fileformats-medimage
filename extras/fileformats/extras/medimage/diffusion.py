import numpy as np
import typing as ty
from pathlib import Path
from fileformats.core import FileSet, extra_implementation
from fileformats.core.sampling import SampleFileGenerator
from fileformats.medimage import DwiEncoding, Bval, Bvec
from fileformats.medimage.diffusion import EncodingArrayType


@extra_implementation(Bval.read_array)
def bval_read_array(bval: Bval) -> EncodingArrayType:
    return np.asarray([float(ln) for ln in bval.read_contents().split()])


@extra_implementation(DwiEncoding.read_encodings)
def bvec_read_array(bvec: Bvec) -> EncodingArrayType:
    bvals = bvec.b_values_file.read_array()
    directions = np.asarray(
        [[float(x) for x in ln.split()] for ln in bvec.read_contents().splitlines()]
    ).T
    return np.concatenate((directions, bvals.reshape((-1, 1))), axis=1)


@extra_implementation(FileSet.generate_sample_data)
def bval_generate_sample_data(
    bval: Bval, generator: SampleFileGenerator
) -> ty.List[Path]:
    bvals_fspath = generator.generate_fspath(Bval)
    bvals = [
        str(generator.rng.randrange(0, 5000))
        for _ in range(generator.rng.randrange(5, 100))
    ]
    with open(bvals_fspath, "w") as f:
        f.write(" ".join(bvals))
    return [bvals_fspath]


@extra_implementation(FileSet.generate_sample_data)
def bvec_generate_sample_data(
    bvec: Bvec, generator: SampleFileGenerator
) -> ty.List[Path]:
    bvecs_fspath = generator.generate_fspath(Bvec)
    bvecs = np.asarray(
        [
            [generator.rng.uniform(0, 1) for _ in range(3)]
            for _ in range(generator.rng.randrange(5, 100))
        ]
    ).T
    # Normalise bvecs
    bvecs = bvecs / np.sqrt(bvecs[0, :] ** 2 + bvecs[1, :] ** 2 + bvecs[2, :] ** 2)
    np.savetxt(bvecs_fspath, bvecs)
    bvals = [str(generator.rng.randrange(0, 5000)) for _ in range(bvecs.shape[1])]
    bvals_fspath = bvecs_fspath.parent / (bvecs_fspath.stem + ".bval")
    with open(bvals_fspath, "w") as f:
        f.write(" ".join(bvals))
    return [bvecs_fspath, bvals_fspath]
