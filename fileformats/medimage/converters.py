from pathlib import Path
import jq
import attrs
import json
import pydra.mark
from pydra.tasks.mrtrix3.utils import MRConvert
from pydra.tasks.dcm2niix import Dcm2Niix
from fileformats.core import mark
from fileformats.medimage.base import MedicalImage
from fileformats.medimage.dicom import Dicom
from fileformats.medimage import (
    Analyze,
    Nifti,
    Nifti_Gzip,
    Nifti_Bids,
    Nifti_Gzip_Bids,
    MrtrixImage,
    MrtrixImageHeader,
)


@mark.converter(source_format=MedicalImage, target_format=Analyze, out_ext=".img")
@mark.converter(source_format=MedicalImage, target_format=MrtrixImage, out_ext=".mif")
@mark.converter(
    source_format=MedicalImage, target_format=MrtrixImageHeader, out_ext=".mif"
)
def mrconvert(out_ext: str):
    return MRConvert(out_file="out" + out_ext)


@mark.converter(source_format=Dicom, target_format=Nifti, out_ext=".img")
@mark.converter(
    source_format=Dicom, target_format=Nifti_Gzip, out_ext=".img", compress="y"
)
@mark.converter(source_format=Dicom, target_format=Nifti_Bids, out_ext=".img")
@mark.converter(
    source_format=Dicom, target_format=Nifti_Gzip_Bids, out_ext=".img", compress="y"
)
def dcm2niix(
    compress="n",
    extract_volume=None,
    file_postfix=attrs.NOTHING,
    side_car_jq=None,
    to_4d=False,
):

    if extract_volume is not None and to_4d:
        raise ValueError(
            f"'extract_volume' ({extract_volume}) and 'to_4d' are mutually exclusive"
        )
    # Create workflow to map input field to "in_file" and optionally perform post-conversion
    # steps to manipulate the converted NIfTI files
    wf = pydra.Workflow(
        name="multistep_conv",
        input_spec=["in_file"],
    )
    wf.add(Dcm2Niix(
        in_dir=wf.lzin.in_file,
        out_dir=".",
        name="dcm2niix",
        compress=compress,
        file_postfix=file_postfix,
    ))
    out_file = wf.dcm2niix.lzout.out_file
    out_json = wf.dcm2niix.lzout.out_json
    # Add MRConvert step to either select a single volume of a 4D dataset or the inverse,
    # wrap a single volume in a 4D dataset
    if extract_volume is not None or to_4d:
        if extract_volume:
            coord = [3, extract_volume]
            axes = [0, 1, 2]
        else:  # to_4d
            coord = attrs.NOTHING
            axes = [0, 1, 2, -1]
        wf.add(
            MRConvert(
                in_file=out_file,
                coord=coord,
                axes=axes,
                name="mrconvert",
            )
        )
        out_file = wf.mrconvert.lzout.out_file
    # Add JQ edit of side car to allow manual fixing of any conversion issues
    if side_car_jq is not None:
        wf.add(
            edit_side_car(in_file=out_json, jq_expr=side_car_jq, name="json_edit")
        )
        out_json = wf.json_edit.lzout.out
    # Set workflow outputs
    wf.set_output(("out_file", out_file))
    wf.set_output(("out_json", out_json))
    wf.set_output(("out_bvec", wf.dcm2niix.lzout.out_bvec))
    wf.set_output(("out_bval", wf.dcm2niix.lzout.out_bval))
    return wf


@pydra.mark.task
def edit_side_car(in_file: Path, jq_expr: str, out_file=None) -> Path:
    """ "Applies ad-hoc edit of JSON side car with JQ query language"""
    if out_file is None:
        out_file = in_file
    with open(in_file) as f:
        dct = json.load(f)
    dct = jq.compile(jq_expr).input(dct).first()
    with open(out_file, "w") as f:
        json.dump(dct, f)
    return in_file
