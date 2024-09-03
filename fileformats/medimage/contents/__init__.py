import typing as ty
from fileformats.core import Classifier


class ContentsClassifier(Classifier):
    description: ty.Optional[str] = None
