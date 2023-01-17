from pathlib import Path
import jq
import attrs
import json
import attrs
import pydra.mark
from pydra.tasks.mrtrix3.utils import MRConvert
from pydra.tasks.dcm2niix import Dcm2Niix
from fileformats.core import mark
from fileformats.medimage.base import MedicalImage
from fileformats.medimage.dicom import Dicom
from fileformats.medimage import Analyze, NeuroImage, Nifti, Nifti_Gzip, MrtrixImage


@mark.converter(target_format=Analyze, out_file="out", out_ext=".img")
@mark.converter(target_format=MrtrixImage, out_file="out", out_ext=".img")
@pydra.mark.task
def mrconvert(in_file: MedicalImage, out_ext: str) -> NeuroImage:
    return MRConvert(in_file=in_file, out_file="out" + out_ext)


@mark.converter(target_format=Nifti, out_file="out", out_ext=".img")
@mark.converter(target_format=Nifti_Gzip, out_file="out", out_ext=".img", compress="y")
def dcm2niix(
    in_file: Dicom,
    extract_volume=None,
    file_postfix=attrs.NOTHING,
    side_car_jq=None,
    to_4d=False,
):
    as_workflow = extract_volume is not None or side_car_jq is not None or to_4d

    if extract_volume is not None and to_4d:
        raise ValueError(
            f"'extract_volume' ({extract_volume}) and 'to_4d' are mutually exclusive"
        )

    in_dir = in_file
    compress = "n"
    if as_workflow:
        wf = pydra.Workflow(
            name="multistep_conv",
            input_spec=["in_dir", "compress"],
            in_dir=in_dir,
            compress=compress,
        )
        in_dir = wf.lzin.in_dir
        compress = wf.lzin.compress
    node = Dcm2Niix(
        in_dir=in_dir,
        out_dir=".",
        name="dcm2niix",
        compress=compress,
        file_postfix=file_postfix,
    )
    if as_workflow:
        wf.add(node)
        out_file = wf.dcm2niix.lzout.out_file
        out_json = wf.dcm2niix.lzout.out_json
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

        if side_car_jq is not None:
            wf.add(
                edit_side_car(
                    in_file=out_json, jq_expr=side_car_jq, name="json_edit"
                )
            )
            out_json = wf.json_edit.lzout.out
        wf.set_output(("out_file", out_file))
        wf.set_output(("out_json", out_json))
        wf.set_output(("out_bvec", wf.dcm2niix.lzout.out_bvec))
        wf.set_output(("out_bval", wf.dcm2niix.lzout.out_bval))
        out = wf, wf.lzout.out_file
    else:
        out = node, node.lzout.out_file
    return out


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
