from fileformats.generic import File


class ListMode(File):

    ext = ".bf"
    binary = True


class Kspace(File):

    binary = True
    iana_mime = None


class TwixVb(Kspace):
    """The format that k-space data is saved in from Siemens scanners
    with system version vB to (at least) vE"""

    ext = ".dat"


# class CustomKspace(Kspace):
#     """A custom format for saving k-space data in binary amd JSON files.

#     Binary files
#     ------------
#     primary : 5-d matrix
#         Data from "data" scan organised in the following dimension order:
#         channel, freq-encode, phase-encode, partition-encode (slice), echoes
#     reference : 5-d matrix
#         Data from calibration scan organised in the same dimension order as
#         primary scan

#     JSON side-car
#     -------------
#     dims : 3-tuple(int)
#         The dimensions of the image in freq, phase, partition (slice) order
#     voxel_size : 3-tuple(float)
#         Size of the voxels in same order as dims
#     num_channels : int
#         Number of channels in the k-space
#     num_echos : int
#         Number of echoes in the acquisition
#     T E : tuple(float)
#         The echo times
#     B0_strength : float
#         Strength of the B0 field
#     B0_dir : 3-tuple(float)
#         Direction of the B0 field
#     larmor_freq : float
#         The central larmor row_frequency of the scanner"""

#     ext = ".ks"
#     side_cars = ("ref", "json")


class Rda(File):
    """MRS format"""

    ext = ".rda"
    binary = True
