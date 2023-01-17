import numpy as np
import nibabel
from fileformats.core import File, FileSet, mark
from fileformats.core.mixin import WithSideCar
from fileformats.text import Json
from fileformats.archive import Gzip
from .base import MedicalImage
from .diffusion import Fslgrad


class NeuroImage(MedicalImage):
    """Imaging formats developed for neuroimaging scans"""


class BaseNifti(NeuroImage):
    def get_header(self):
        return dict(nibabel.load(self.fspath).header)

    def get_array(self):
        return nibabel.load(self.fspath).get_data()

    def get_vox_sizes(self):
        # FIXME: This won't work for 4-D files
        return self.get_header()["pixdim"][1:4]

    def get_dims(self):
        # FIXME: This won't work for 4-D files
        return self.get_header()["dim"][1:4]


class WithBids(WithSideCar):

    side_car_type = Json


class Nifti(BaseNifti):

    ext = ".nii"
    iana = "application/x-nifti"


class Nifti_Gzip(BaseNifti, Gzip):

    ext = ".nii.gz"
    iana = "application/x-nifti+gzip"


class NiftiX(WithBids, Nifti):
    iana = "application/x-nifti+bids"


class NiftiX_Gzip(WithBids, Nifti_Gzip):
    iana = "application/x-nifti+bids.gzip"


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


class NiftiXFslgrad(NiftiX, WithFslgrad):
    iana = "application/x-nifti+bids.fslgrad"


class NiftiGzXFslgrad(NiftiX_Gzip, WithFslgrad):
    iana = "application/x-nifti+bids.gzip.fslgrad"


class MrtrixImage(NeuroImage):

    ext = ".mif"

    def _load_header_and_array(self):
        with open(self.path, "rb") as f:
            contents = f.read()
        hdr_end = contents.find(b"\nEND\n")
        hdr_contents = contents[:hdr_end].decode("utf-8")
        hdr = dict(ln.split(": ", maxsplit=1) for ln in hdr_contents.split("\n"))
        for key, value in list(hdr.items()):
            if "," in value:
                try:
                    hdr[key] = np.array(value.split(","), datatype=int)
                except ValueError:
                    try:
                        hdr[key] = np.array(value.split(","), datatype=float)
                    except ValueError:
                        pass
            else:
                try:
                    hdr[key] = int(value)
                except ValueError:
                    try:
                        hdr[key] = float(value)
                    except ValueError:
                        pass
        del hdr["mrtrix image"]  # Delete "magic line" at start of header
        array_start = int(hdr["file"].split()[1])
        array = np.asarray(contents[array_start:])
        dim = [hdr["dim"][int(ln[1])] for ln in hdr["layout"]]
        array = array.reshape(dim)
        return hdr, array

    def get_header(self):
        return self._load_header_and_array(self)[0]

    def get_array(self):
        return self._load_header_and_array(self)[1]

    def get_vox_sizes(self):
        return self.get_header(self)["vox"]

    def get_dims(self):
        return self.get_header(self)["dim"]


# =====================================================================
# All Data Formats
# =====================================================================


class AnalyzeHeader(File):

    ext = ".hdr"


class Analyze(WithSideCar, NeuroImage):

    ext = ".img"
    side_car_type = AnalyzeHeader

    def get_array(self):
        raise NotImplementedError

    def get_header(self):
        raise NotImplementedError
