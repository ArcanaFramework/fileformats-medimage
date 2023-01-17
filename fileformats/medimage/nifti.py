import nibabel
from fileformats.core.mixin import WithSideCar
from fileformats.text import Json
from fileformats.archive import Gzip
from .base import NeuroImage


class BaseNifti(NeuroImage):
    def load_metadata(self):
        return dict(nibabel.load(self.fspath).header)

    @property
    def data_array(self):
        return nibabel.load(self.fspath).get_data()

    @property
    def vox_sizes(self):
        # FIXME: This won't work for 4-D files
        return self.metadata["pixdim"][1:4]

    @property
    def dims(self):
        # FIXME: This won't work for 4-D files
        return self.metadata["dim"][1:4]


class WithBids(WithSideCar):

    side_car_type = Json


class Nifti(BaseNifti):

    ext = ".nii"
    iana = "application/x-nifti"


class Nifti_Gzip(BaseNifti, Gzip):

    ext = ".nii.gz"
    iana = "application/x-nifti+gzip"


class Nifti_Bids(WithBids, Nifti):
    iana = "application/x-nifti+bids"


class Nifti_Gzip_Bids(WithBids, Nifti_Gzip):
    iana = "application/x-nifti+gzip.bids"
