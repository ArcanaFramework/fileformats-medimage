from fileformats.medimage import (
    NiftiGzX,
    NiftiGzXBvec,
    T1w,
    Dmri,
    Fmri,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetListMode,
    Vnd_Siemens_Biograph128Vision_Vr20b_PetCountRate,
)


def test_t1w_generator():
    img = NiftiGzX[T1w].sample()
    assert len(img.dims()) == 3


def test_fmri_generator():
    img = NiftiGzX[Fmri].sample()
    assert len(img.dims()) == 4


def test_dmri_generator():
    img = NiftiGzXBvec[Dmri].sample()
    assert len(img.dims()) == 4


def test_siemens_pet_listmode_generator():
    img = Vnd_Siemens_Biograph128Vision_Vr20b_PetListMode.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"


def test_siemens_pet_countrate_generator():
    img = Vnd_Siemens_Biograph128Vision_Vr20b_PetCountRate.sample()
    assert img.metadata["PatientName"] == "FirstName^LastName"
