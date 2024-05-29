from fileformats.core import from_mime
from fileformats.medimage import (
    NiftiGz,
    NiftiGzX,
    T1w,
)


def test_image_contents1():
    assert from_mime("medimage/t1w+nifti-gz") == NiftiGz[T1w]


def test_image_contents_generation():
    img = NiftiGzX[T1w].sample()
    assert len(img.dims()) == 3
