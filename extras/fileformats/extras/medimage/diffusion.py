import numpy as np
from fileformats.medimage import DwiEncoding, Bval, Bvec


@Bval.read_array.register
def bval_read_array(bval: Bval) -> np.ndarray:  # noqa
    return np.asarray([float(ln) for ln in bval.read_contents().split()])


@DwiEncoding.read_array.register
def bvec_read_array(bvec: Bvec) -> np.ndarray:  # noqa
    bvals = bvec.b_values_file.read_array()
    directions = np.asarray(
        [[float(x) for x in ln.split()] for ln in bvec.read_contents().splitlines()]
    ).T
    return np.concatenate((directions, bvals.reshape((-1, 1))), axis=1)  # type: ignore
