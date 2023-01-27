import numpy as np
from fileformats.core import mark
from fileformats.core.mixin import WithAdjacentFiles
from fileformats.generic import File
from .nifti import NiftiGzX, NiftiGz, Nifti2, NiftiX


class DwiEncoding(File):

    iana_mime = None

    @property
    def array(self):
        "Both the gradient direction and weighting combined into a single Nx4 array"
        raise NotImplementedError(
            f"array property hasn't been implemented for {type(self)} diffusion encoding subclass"
        )

    @property
    def grads(self):
        "Both the gradient direction and weighting combined into a single Nx4 array"
        raise NotImplementedError(
            f"array property hasn't been implemented for {type(self)} diffusion encoding subclass"
        )

    @property
    def bvals(self):
        raise NotImplementedError(
            f"array property hasn't been implemented for {type(self)} diffusion encoding subclass"
        )


class Bval(File):

    ext = ".bval"

    @property
    def array(self):
        return np.asarray([float(ln) for ln in self.read_contents().split()])


class Bvec(WithAdjacentFiles, DwiEncoding):
    """FSL-style diffusion encoding, in two separate files"""

    ext = ".bvec"
    header_type = Bval

    @property
    def array(self):
        return np.concatenate(self.bvecs, self.bvals)

    @mark.required
    @property
    def bvals_file(self) -> Bval:
        return self.select_by_ext(Bval)

    @property
    def grads(self):
        return np.asarray(
            [float(x) for x in ln.split()]
            for ln in self.read_contents().splitlines()
        )

    @property
    def bvals(self):
        return self.bvals_file.array


class Bfile(DwiEncoding):
    """MRtrix-style diffusion encoding, all in one file"""

    ext = ".b"

    @property
    def array(self):
        return np.asarray(
            [float(x) for x in ln.split()] for ln in self.read_contents().splitlines()
        )

    @property
    def grads(self):
        return self.array[:, :3]

    @property
    def bvals(self):
        return self.array[:, 3]


# NIfTI file format gzipped with BIDS side car
class WithBvec(WithAdjacentFiles):
    @mark.required
    @property
    def encoding(self):
        return self.select_by_ext(Bvec)


# NIfTI file format gzipped with BIDS side car
class WithBfile(WithAdjacentFiles):
    @mark.required
    @property
    def encoding(self):
        return self.select_by_ext(Bfile)


class NiftiBvec(WithBvec, Nifti2):
    iana_mime = "application/x-nifti2+bvec"


class NiftiGzBvec(WithBvec, NiftiGz, WithBvec):
    iana_mime = "application/x-nifti2+gzip.bvec"


class NiftiXBvec(WithBvec, NiftiX):
    iana_mime = "application/x-nifti2+json.bvec"


class NiftiGzXBvec(WithBvec, NiftiGzX):
    iana_mime = "application/x-nifti2+gzip.json.bvec"


class NiftiB(WithBfile, Nifti2):
    iana_mime = "application/x-nifti2+b"


class NiftiGzB(WithBfile, NiftiGz, WithBvec):
    iana_mime = "application/x-nifti2+gzip.b"


class NiftiXB(WithBfile, NiftiX):
    iana_mime = "application/x-nifti2+json.b"


class NiftiGzXB(WithBfile, NiftiGzX):
    iana_mime = "application/x-nifti2+gzip.json.b"


# Track files


class MrtrixTrack(File):

    ext = ".tck"
