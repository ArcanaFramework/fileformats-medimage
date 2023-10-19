from fileformats.generic import File


class Kspace(File):

    binary = True
    iana_mime = None


class Rda(File):
    """MRS format"""

    ext = ".rda"
    binary = True
