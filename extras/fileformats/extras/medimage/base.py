import typing as ty
from pathlib import Path
import tempfile
from fileformats.core import extra_implementation, FileSet
from fileformats.medimage import MedicalImage


@extra_implementation(MedicalImage.deidentify)
def dicom_deidentify(
    image: MedicalImage,
    out_dir: ty.Optional[Path] = None,
    new_stem: ty.Optional[str] = None,
    copy_mode: FileSet.CopyMode = FileSet.CopyMode.copy,
) -> MedicalImage:
    """Assume that no deidentification is needed for medical images by default. We make a
    copy of the image in the output directory for consistency with the behavior of other
    deidentification formats"""
    if out_dir is None:
        out_dir = Path(tempfile.mkdtemp())
    out_dir.mkdir(exist_ok=True, parents=True)
    image.copy(out_dir, new_stem=new_stem, mode=copy_mode)
    return image
