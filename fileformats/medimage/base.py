import numpy as np
from fileformats.generic import File


# =====================================================================
# Custom loader functions for different image types
# =====================================================================


class MedicalImage(File):

    iana_mime = None
    INCLUDE_HDR_KEYS = None
    IGNORE_HDR_KEYS = None

    @property
    def data_array(self):
        """
        Returns the binary data of the image in a numpy array
        """
        raise NotImplementedError

    def contents_equal(self, other_image, rms_tol=None, **kwargs):
        """
        Test whether the (relevant) contents of two image self are equal
        given specific criteria

        Parameters
        ----------
        other_image : Fileset
            The other self to compare
        rms_tol : float
            The root-mean-square tolerance that is acceptable between the array
            data for the images to be considered equal
        """
        if type(other_image) != type(self):
            return False
        if self.headers_diff(self, other_image, **kwargs):
            return False
        if rms_tol:
            rms_diff = self.rms_diff(self, other_image)
            return rms_diff < rms_tol
        else:
            return np.array_equiv(self.get_array(), other_image.get_array())

    def metadata_diff(self, other_image, include_keys=None, ignore_keys=None, **kwargs):
        """
        Check headers to see if all values
        """
        diff = []
        hdr = self.get_header()
        hdr_keys = set(hdr.keys())
        other_hdr = other_image.get_header()
        if include_keys is not None:
            if ignore_keys is not None:
                raise ValueError(
                    "Doesn't make sense to provide both 'include_keys' ({}) "
                    "and ignore_keys ({}) to headers_equal method".format(
                        include_keys, ignore_keys
                    )
                )
            include_keys &= hdr_keys
        elif ignore_keys is not None:
            include_keys = hdr_keys - set(ignore_keys)
        else:
            if self.INCLUDE_HDR_KEYS is not None:
                if self.IGNORE_HDR_KEYS is not None:
                    raise ValueError(
                        "Doesn't make sense to have both 'INCLUDE_HDR_FIELDS'"
                        "and 'IGNORE_HDR_FIELDS' class attributes of class {}".format(
                            type(self).__name__
                        )
                    )
                include_keys = self.INCLUDE_HDR_KEYS  # noqa pylint: disable=no-member
            elif self.IGNORE_HDR_KEYS is not None:
                include_keys = hdr_keys - set(self.IGNORE_HDR_KEYS)
            else:
                include_keys = hdr_keys
        for key in include_keys:
            value = hdr[key]
            try:
                other_value = other_hdr[key]
            except KeyError:
                diff.append(key)
            else:
                if isinstance(value, np.ndarray):
                    if not isinstance(other_value, np.ndarray):
                        diff.append(key)
                    else:
                        try:
                            if not np.allclose(value, other_value, equal_nan=True):
                                diff.append(key)
                        except TypeError:
                            # Fallback to a straight comparison for some formats
                            if value != other_value:
                                diff.append(key)
                elif value != other_value:
                    diff.append(key)
        return diff

    def rms_diff(self, other_image):
        """
        Return the RMS difference between the image arrays
        """
        return np.sqrt(np.sum((self.get_array() - other_image.get_array()) ** 2))


class NeuroImage(MedicalImage):
    """Imaging formats developed for neuroimaging scans"""
    iana_mime = None
