from fileformats.medimage import (
    NiftiGzX,
    NiftiGzXBvec,
    T1w,
    Dmri,
    Fmri,
    # Vnd_Siemens_Biograph128Vision_Vr20b_PetListMode,
    # Vnd_Siemens_Biograph128Vision_Vr20b_PetCountRate,
    # Vnd_Siemens_Biograph128Vision_Vr20b_PetSinogram,
    # Vnd_Siemens_Biograph128Vision_Vr20b_PetDynamicSinogramSeries,
    # Vnd_Siemens_Biograph128Vision_Vr20b_PetNormalisation,
    # Vnd_Siemens_Biograph128Vision_Vr20b_PetParameterisation,
    # Vnd_Siemens_Biograph128Vision_Vr20b_PetCtSpl,
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


# def test_siemens_pet_listmode_generator():
#     img = Vnd_Siemens_Biograph128Vision_Vr20b_PetListMode.sample()
#     assert img.metadata["PatientName"] == "FirstName^LastName"


# def test_siemens_pet_countrate_generator():
#     img = Vnd_Siemens_Biograph128Vision_Vr20b_PetCountRate.sample()
#     assert img.metadata["PatientName"] == "FirstName^LastName"


# def test_siemens_pet_sinogram_generator():
#     img = Vnd_Siemens_Biograph128Vision_Vr20b_PetSinogram.sample()
#     assert img.metadata["PatientName"] == "FirstName^LastName"


# def test_siemens_pet_dynamics_sino_generator():
#     img = Vnd_Siemens_Biograph128Vision_Vr20b_PetDynamicSinogramSeries.sample()
#     assert img.metadata["PatientName"] == "FirstName^LastName"


# def test_siemens_pet_normalisation_generator():
#     img = Vnd_Siemens_Biograph128Vision_Vr20b_PetNormalisation.sample()
#     assert img.metadata["PatientName"] == "FirstName^LastName"


# def test_siemens_pet_petct_spl_generator():
#     img = Vnd_Siemens_Biograph128Vision_Vr20b_PetCtSpl.sample()
#     assert img.metadata["PatientName"] == "FirstName^LastName"


# def test_siemens_pet_parameterisation_generator():
#     img = Vnd_Siemens_Biograph128Vision_Vr20b_PetParameterisation.sample()
#     assert img.metadata["PatientName"] == "FirstName^LastName"
