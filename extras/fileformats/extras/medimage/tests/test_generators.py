import numpy as np
import pytest

from fileformats.medimage import (
    NiftiGzX,
    NiftiGzXBvec,
    T1w,
    Dmri,
    Fmri,
    Bval,
    Bvec,
)


@pytest.mark.xfail(reason="There is a bug in medimages4tests")
def test_t1w_generator():
    img = NiftiGzX[T1w].sample()
    assert len(img.dims()) == 3


@pytest.mark.xfail(reason="There is a bug in medimages4tests")
def test_fmri_generator():
    img = NiftiGzX[Fmri].sample()
    assert len(img.dims()) == 4


@pytest.mark.xfail(reason="There is a bug in medimages4tests")
def test_dmri_generator():
    img = NiftiGzXBvec[Dmri].sample()
    assert len(img.dims()) == 4


def test_bval_generator():
    bval = Bval.sample()
    assert len(bval.read_array()) >= 5


def test_bvec_generator():
    bvec = Bvec.sample()
    n, m = bvec.encodings_array.shape
    assert n >= 5
    assert m == 4
