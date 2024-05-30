from fileformats.medimage import NiftiGzX, NiftiGzXBvec, T1w, Dmri, Fmri


def test_t1w_generator():
    img = NiftiGzX[T1w].sample()
    assert len(img.dims()) == 3


def test_fmri_generator():
    img = NiftiGzX[Fmri].sample()
    assert len(img.dims()) == 4


def test_dmri_generator():
    img = NiftiGzXBvec[Dmri].sample()
    assert len(img.dims()) == 4
