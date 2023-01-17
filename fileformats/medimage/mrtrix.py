from pathlib import Path
import numpy as np
from fileformats.core import mark
from fileformats.core.mixin import WithMagic
from fileformats.numeric import DataFile
from fileformats.core.exceptions import FormatMismatchError
from .misc import NeuroImage


class BaseMrtrixImage(NeuroImage, WithMagic):

    magic = b"mrtix image\n"

    def load_metadata(self):
        metadata = {}
        with open(self.fspath, "rb") as f:
            line = f.readline()
            assert line == self.magic
            line = f.readline()
            while line != b"END\n":
                key, value = line.split(": ", maxsplit=1)
                key = key.decode("utf-8")
                value = value.decode("utf-8")  # convert to unicode
                if "," in value:
                    try:
                        value = np.array(value.split(","), datatype=int)
                    except ValueError:
                        try:
                            value = np.array(value.split(","), datatype=float)
                        except ValueError:
                            pass
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                metadata[key] = value
        return metadata

    @property
    def data_fspath(self):
        data_fspath = self.metadata["file"].split()[0]
        if data_fspath == ".":
            data_fspath = self.fspath
        else:
            data_fspath = Path(data_fspath).relative_to(self.fspath.parent)
        return data_fspath

    @property
    def data_offset(self):
        return int(self.metadata["file"].split()[1])

    @property
    def vox_sizes(self):
        return self.metadata["vox"]

    @property
    def dims(self):
        return self.metadata["dim"]

    @property
    def data_array(self):
        data = self.read_contents(offset=self.data_offset)
        array = np.asarray(data)
        data_array = array.reshape(self.dims)
        raise NotImplementedError(
            "Need to work out how to use the metadata to read the array in the correct order"
        )
        return data_array


class MrtrixImage(BaseMrtrixImage):

    ext = ".mif"

    @mark.check
    def check_data_file(self):
        if self.data_fspath != self.fspath:
            raise FormatMismatchError(
                f"Data file ('{self.data_fspath}') is not set to the same file as header "
                f"('{self.fspath}')")

    @property
    def data_file(self):
        return self


class MrtrixImageHeader(BaseMrtrixImage):

    ext = ".mih"

    @mark.required
    @property
    def data_file(self):
        return DataFile(self.data_fspath)

    @classmethod
    def from_primary(cls, fspath):
        base_image = BaseMrtrixImage(fspath)
        return cls([base_image.fspath, base_image.data_fspath])
