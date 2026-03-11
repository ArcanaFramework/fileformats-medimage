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
    dest = generator.generate_fspath(Bval)
    bvals = [
        str(generator.rng.randrange(0, 5000))
        for _ in range(generator.rng.randrange(0, 100))
    ]
    with open(dest, "w") as f:
        f.write(" ".join(bvals))
    return [dest]


@extra_implementation(FileSet.generate_sample_data)
def bvec_generate_sample_data(
    bvec: Bvec, generator: SampleFileGenerator
) -> ty.List[Path]:
    dest = generator.generate_fspath(Bvec)
    bvecs = np.asarray(
        [
            [generator.rng.uniform(0, 1) for _ in range(3)]
            for _ in range(generator.rng.randrange(0, 100))
        ]
    )
    # Normalise bvecs
    bvecs = bvecs / np.sqrt(bvecs[0, :] ** 2 + bvecs[1, :] ** 2 + bvecs[2, :] ** 2)
    np.savetxt(dest, bvecs)
    bvals_fspath = 
    return [dest]
