import numpy as np
from fileformats.core import FileSet, File, mark
from .misc import BaseNifti, NiftiX_Gzip, Nifti_Gzip, Nifti, NiftiX


class DwiEncoding(FileSet):
    @property
    def dirs(self):
        raise NotImplementedError

    @property
    def b(self):
        raise NotImplementedError


class Bvec(File):

    ext = ".bvec"

    @property
    def array(self):
        return np.asarray(
            [float(x) for x in ln.split()] for ln in self.read_contents().splitlines()
        )


class Bval(File):

    ext = ".bval"

    @property
    def array(self):
        return np.asarray(float(ln) for ln in self.read_contents().splitlines())


class Fslgrad(DwiEncoding):
    @mark.required
    @property
    def bvecs(self):
        return Bvec(self.select_by_ext(Bvec))

    @mark.required
    @property
    def bvals(self):
        return Bval(self.select_by_ext(Bval))

    @property
    def dirs(self):
        return self.bvecs.array

    @property
    def b(self):
        return self.bvals.array


class Mrtrixgrad(File, DwiEncoding):

    ext = ".b"

    @property
    def array(self):
        return np.asarray(
            [float(x) for x in ln.split()] for ln in self.read_contents().splitlines()
        )

    @property
    def dirs(self):
        return self.array[:, :3]

    @property
    def b(self):
        return self.array[:, 3]


# NIfTI file format gzipped with BIDS side car
class WithFslgrad(BaseNifti, Fslgrad):
    @mark.required
    @property
    def grads(self):
        return Fslgrad(self.fspaths)


class Nifti_Fslgrad(Nifti, WithFslgrad):
    iana = "application/x-nifti+fslgrad"


class Nifti_Gzip_Fslgrad(Nifti_Gzip, WithFslgrad):
    iana = "application/x-nifti+gzip.fslgrad"


class Nifti_Bids_Fslgrad(NiftiX, WithFslgrad):
    iana = "application/x-nifti+bids.fslgrad"


class Nifti_Gzip_Bids_Fslgrad(NiftiX_Gzip, WithFslgrad):
    iana = "application/x-nifti+gzip.bids.fslgrad"


# Track files

class MrtrixTrack(File):

    ext = ".tck"