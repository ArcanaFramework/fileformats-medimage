import numpy as np
from fileformats.core import FileSet, File, mark


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


# Track files


class MrtrixTrack(File):

    ext = ".tck"
