import pytest

from fileformats.core import from_mime
from fileformats.medimage import (
    NiftiGz,
    NiftiGzX,
    T1w,
)


def test_image_contents1():
    assert from_mime("medimage/t1w+nifti-gz") == NiftiGz[T1w]


@pytest.mark.xfail(reason="There is a bug in medimages4tests")
def test_image_contents_generation() -> None:
    img = NiftiGzX[T1w].sample()
    assert len(img.dims()) == 3
