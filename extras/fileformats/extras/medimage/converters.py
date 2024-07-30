from pathlib import Path
import attrs
import json
import typing as ty
import tempfile
from fileformats.core import hook
import pydra
from fileformats.medimage.base import MedicalImage
from fileformats.medimage.dicom import DicomDir, DicomCollection, DicomSeries
from fileformats.medimage import (
    Analyze,
    Nifti,
    NiftiGz,
    NiftiX,
    NiftiGzX,
    NiftiXBvec,
    NiftiBvec,
    NiftiGzBvec,
    NiftiGzXBvec,
)

from pydra.tasks.mrtrix3.latest import MrConvert
from pydra.tasks.dcm2niix import Dcm2Niix


@hook.converter(source_format=MedicalImage, target_format=Analyze, out_ext=Analyze.ext)
def mrconvert(name, out_ext: str):
    """Initiate an MRConvert task with the output file extension set

    Parameters
    ----------
    name : str
        name of the converter task
    out_ext : str
        extension of the output file, used by MRConvert to determine the desired format

    Returns
    -------
    pydra.ShellCommandTask
        the converter task
    """
    return MrConvert(name=name, out_file="out" + out_ext)


@pydra.mark.task
def ensure_dicom_dir(dicom: DicomCollection) -> DicomDir:
    if isinstance(dicom, DicomSeries):
        dicom_dir_fspath = tempfile.mkdtemp()
        dicom.copy(dicom_dir_fspath, mode=DicomDir.CopyMode.link)
        dicom = DicomDir(dicom_dir_fspath)
    elif not isinstance(dicom, DicomDir):
        raise RuntimeError(
            "Unrecognised input to ensure_dicom_dir, should be DicomSeries or DicomDir "
            f"not {dicom}"
        )
    return dicom


@hook.converter(source_format=DicomCollection, target_format=Nifti)
@hook.converter(source_format=DicomCollection, target_format=NiftiGz, compress="y")
@hook.converter(source_format=DicomCollection, target_format=NiftiX)
@hook.converter(source_format=DicomCollection, target_format=NiftiGzX, compress="y")
@hook.converter(source_format=DicomCollection, target_format=NiftiXBvec)
@hook.converter(source_format=DicomCollection, target_format=NiftiBvec)
@hook.converter(source_format=DicomCollection, target_format=NiftiGzBvec)
@hook.converter(source_format=DicomCollection, target_format=NiftiGzXBvec, compress="y")
def extended_dcm2niix(
    name,
    compress: str = "n",
    file_postfix: ty.Optional[str] = None,
    side_car_jq: ty.Optional[str] = None,
    extract_volume: ty.Optional[int] = None,
    to_4d: bool = False,
):
    """The Dcm2niix command wrapped in a workflow in order to map the inputs and outputs
    onto "in_file" and "out_file", respectively, and implement optional post-conversion
    manipulations to allow manual override of conversion issues.

    Parameters
    ----------
    name : str
        name of the workflow
    compress : str, optional
        whether to apply compression to the conversion, by default "n"
    file_postfix : str, optional
        select one of the multiple output files by its generated postfix.
        See https://github.com/rordenlab/dcm2niix/blob/master/FILENAMING.md for
        complete list of different postfixes that will be generated, by default None
    side_car_jq : str, optional
        JQ (https://stedolan.github.io/jq/) expression that can be provided to edit
        the resulting JSON side-car. Can be used to fix any conversion issues or add
        required fields manually, by default None
    extract_volume : int, optional
        extract a 3D volume from a 4D dataset by passing the index (0-based) of the
        volume to extract, by default None
    to_4d : bool, optional
        whether to wrap resulting 3D NIfTI volume in a 4D dataset, by default False

    Returns
    -------
    pydra.Workflow
        the converter workflow

    Raises
    ------
    ValueError
        when mutually exclusive "extract_volume" and "to_4d" options are provided
    """

    if extract_volume is not None and to_4d:
        raise ValueError(
            f"'extract_volume' ({extract_volume}) and 'to_4d' are mutually exclusive"
        )
    # Create workflow to map input field to "in_file" and optionally perform post-conversion
    # steps to manipulate the converted NIfTI files
    wf = pydra.Workflow(
        name=name,
        input_spec=["in_file"],
    )
    wf.add(
        ensure_dicom_dir(
            dicom=wf.lzin.in_file,
            name="ensure_dicom_dir",
        )
    )

    if file_postfix is None:
        file_postfix = attrs.NOTHING  # type: ignore
    wf.add(
        Dcm2Niix(
            in_dir=wf.ensure_dicom_dir.lzout.out,
            out_dir=Path("."),
            name="dcm2niix",
            compress=compress,
            file_postfix=file_postfix,
        )
    )
    out_file = wf.dcm2niix.lzout.out_file
    out_json = wf.dcm2niix.lzout.out_json
    # Add MRConvert step to either select a single volume of a 4D dataset or the inverse,
    # wrap a single volume in a 4D dataset
    if extract_volume is not None or to_4d:
        if extract_volume:
            coord = (3, extract_volume)
            axes = [0, 1, 2]
        else:  # to_4d
            coord = attrs.NOTHING  # type: ignore
            axes = [0, 1, 2, -1]
        wf.add(
            MrConvert(
                in_file=out_file,
                out_file="out" + NiftiGzX.ext,
                coord=coord,
                axes=axes,
                name="mrconvert",
            )
        )
        out_file = wf.mrconvert.lzout.out_file
    # Add JQ edit of side car to allow manual fixing of any conversion issues
    if side_car_jq is not None:
        wf.add(
            edit_dcm2niix_side_car(
                in_file=out_json, jq_expr=side_car_jq, name="json_edit"
            )
        )
        out_json = wf.json_edit.lzout.out

    wf.add(
        collect_dcm2niix_outputs(
            name="collect_outputs",
            out_file=out_file,
            out_json=out_json,
            out_bvec=wf.dcm2niix.lzout.out_bvec,
            out_bval=wf.dcm2niix.lzout.out_bval,
        )
    )
    # Set workflow outputs
    wf.set_output(("out_file", wf.collect_outputs.lzout.out))
    return wf


@pydra.mark.task
def edit_dcm2niix_side_car(in_file: Path, jq_expr: str, out_file=None) -> Path:
    """ "Applies ad-hoc edit of JSON side car with JQ query language"""
    if out_file is None:
        out_file = in_file
    with open(in_file) as f:
        dct = json.load(f)
    try:
        import jq
    except ImportError:
        raise RuntimeError(
            "Cannot edit dcm2niix file with jq expression as `jq` package is not "
            "available in the current environment. It is planned to replace "
            "this dependency as it does not install on Windows easily, but for now you "
            "can enable this feature by installing `jq` with `pip install jq`"
        )
    dct = jq.compile(jq_expr).input(dct).first()
    with open(out_file, "w") as f:
        json.dump(dct, f)
    return in_file


@pydra.mark.task
def collect_dcm2niix_outputs(
    out_file: Path, out_json: Path, out_bvec: Path, out_bval: Path
) -> ty.List[Path]:
    lst = [out_file]
    for file in (out_json, out_bvec, out_bval):
        if file is not attrs.NOTHING:
            lst.append(file)
    return lst
