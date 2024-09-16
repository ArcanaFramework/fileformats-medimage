import numpy as np
import typing  # noqa: F401
import numpy.typing
from fileformats.core import extra_implementation
from fileformats.medimage import DwiEncoding, Bval, Bvec
from fileformats.medimage.diffusion import EncodingArrayType


@extra_implementation(Bval.read_array)
def bval_read_array(bval: Bval) -> EncodingArrayType:
    return np.asarray([float(ln) for ln in bval.read_contents().split()])


@extra_implementation(DwiEncoding.read_array)
def bvec_read_array(bvec: Bvec) -> EncodingArrayType:
    bvals = bvec.b_values_file.read_array()
    directions = np.asarray(
        [[float(x) for x in ln.split()] for ln in bvec.read_contents().splitlines()]
    ).T
    return np.concatenate((directions, bvals.reshape((-1, 1))), axis=1)
