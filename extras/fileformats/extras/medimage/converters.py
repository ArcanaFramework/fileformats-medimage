from pathlib import Path
import attrs
import json
import typing as ty
import tempfile
from fileformats.core import converter
from pydra.design import python, workflow, shell
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
from fileformats.core.typing import PathType
from pydra.tasks.dcm2niix import Dcm2Niix
from pydra.utils.typing import MultiInputObj
from fileformats.generic import File, Directory  # noqa: F401
from fileformats.medimage_mrtrix3 import ImageIn, ImageOut, Tracks  # noqa: F401


@python.define  # type: ignore[misc]
def EnsureDicomDir(dicom: DicomCollection) -> DicomDir:
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


@converter(source_format=DicomCollection, target_format=Nifti)
@converter(source_format=DicomCollection, target_format=NiftiGz, compress="y")
@converter(source_format=DicomCollection, target_format=NiftiX)
@converter(source_format=DicomCollection, target_format=NiftiGzX, compress="y")
@converter(source_format=DicomCollection, target_format=NiftiXBvec)
@converter(source_format=DicomCollection, target_format=NiftiBvec)
@converter(source_format=DicomCollection, target_format=NiftiGzBvec)
@converter(source_format=DicomCollection, target_format=NiftiGzXBvec, compress="y")
@workflow.define  # type: ignore[misc]
def ExtendedDcm2niix(
    in_file: DicomCollection,
    compress: str = "n",
    file_postfix: ty.Optional[str] = None,
    side_car_jq: ty.Optional[str] = None,
    extract_volume: ty.Optional[int] = None,
    to_4d: bool = False,
) -> ty.List[Path]:
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
    out_file: list[Path]
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
    ensure_dicom_dir = workflow.add(EnsureDicomDir(dicom=in_file))

    if file_postfix is None:
        file_postfix = attrs.NOTHING  # type: ignore
    dcm2niix = workflow.add(
        Dcm2Niix(
            in_dir=ensure_dicom_dir.out,
            out_dir=Path("."),
            name="dcm2niix",
            compress=compress,
            file_postfix=file_postfix,
        )
    )
    out_file = dcm2niix.out_file
    out_json = dcm2niix.out_json
    # Add MRConvert step to either select a single volume of a 4D dataset or the inverse,
    # wrap a single volume in a 4D dataset
    if extract_volume is not None or to_4d:
        if extract_volume:
            coord = (3, extract_volume)
            axes = [0, 1, 2]
        else:  # to_4d
            coord = attrs.NOTHING  # type: ignore
            axes = [0, 1, 2, -1]
        mrconvert = workflow.add(
            MrConvert(  # type: ignore[call-arg]
                in_file=out_file,
                out_file="out" + NiftiGzX.ext,
                coord=coord,
                axes=axes,
            )
        )
        out_file = mrconvert.out_file
    # Add JQ edit of side car to allow manual fixing of any conversion issues
    if side_car_jq is not None:
        json_edit = workflow.add(
            EditDcm2niixSideCar(in_file=out_json, jq_expr=side_car_jq, name="json_edit")
        )
        out_json = json_edit.out

    collect_outputs = workflow.add(
        CollectDcm2niixOutputs(
            out_file=out_file,
            out_json=out_json,
            out_bvec=dcm2niix.out_bvec,
            out_bval=dcm2niix.out_bval,
        )
    )
    # Set workflow outputs
    return collect_outputs.out  # type: ignore[no-any-return]


@python.define  # type: ignore[misc]
def EditDcm2niixSideCar(
    in_file: Path, jq_expr: str, out_file: ty.Optional[PathType] = None
) -> Path:
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


@python.define  # type: ignore[misc]
def CollectDcm2niixOutputs(
    out_file: Path, out_json: Path, out_bvec: Path, out_bval: Path
) -> ty.List[Path]:
    lst = [out_file]
    for file in (out_json, out_bvec, out_bval):
        if file is not attrs.NOTHING:  # type: ignore[comparison-overlap]
            lst.append(file)
    return lst


@converter(source_format=MedicalImage, target_format=Analyze, out_ext=Analyze.ext)
@shell.define
class MrConvert:
    """If used correctly, this program can be a very useful workhorse. In addition to converting images between different formats, it can be used to extract specific studies from a data set, extract a specific region of interest, or flip the images. Some of the possible operations are described in more detail below.

        Note that for both the -coord and -axes options, indexing starts from 0 rather than 1. E.g. -coord 3 <#> selects volumes (the fourth dimension) from the series; -axes 0,1,2 includes only the three spatial axes in the output image.

        Additionally, for the second input to the -coord option and the -axes option, you can use any valid number sequence in the selection, as well as the 'end' keyword (see the main documentation for details); this can be particularly useful to select multiple coordinates.

        The -vox option is used to change the size of the voxels in the output image as reported in the image header; note however that this does not re-sample the image based on a new voxel size (that is done using the mrgrid command).

        By default, the intensity scaling parameters in the input image header are passed through to the output image header when writing to an integer image, and reset to 0,1 (i.e. no scaling) for floating-point and binary images. Note that the -scaling option will therefore have no effect for floating-point or binary output images.

        The -axes option specifies which axes from the input image will be used to form the output image. This allows the permutation, omission, or addition of axes into the output image. The axes should be supplied as a comma-separated list of axis indices. If an axis from the input image is to be omitted from the output image, it must either already have a size of 1, or a single coordinate along that axis must be selected by the user by using the -coord option. Examples are provided further below.

        The -bvalue_scaling option controls an aspect of the import of diffusion gradient tables. When the input diffusion-weighting direction vectors have norms that differ substantially from unity, the b-values will be scaled by the square of their corresponding vector norm (this is how multi-shell acquisitions are frequently achieved on scanner platforms). However in some rare instances, the b-values may be correct, despite the vectors not being of unit norm (or conversely, the b-values may need to be rescaled even though the vectors are close to unit norm). This option allows the user to control this operation and override MRrtix3's automatic detection.


        Example usages
        --------------


        Extract the first volume from a 4D image, and make the output a 3D image:

            `$ mrconvert in.mif -coord 3 0 -axes 0,1,2 out.mif`

            The -coord 3 0 option extracts, from axis number 3 (which is the fourth axis since counting begins from 0; this is the axis that steps across image volumes), only coordinate number 0 (i.e. the first volume). The -axes 0,1,2 ensures that only the first three axes (i.e. the spatial axes) are retained; if this option were not used in this example, then image out.mif would be a 4D image, but it would only consist of a single volume, and mrinfo would report its size along the fourth axis as 1.


        Extract slice number 24 along the AP direction:

            `$ mrconvert volume.mif slice.mif -coord 1 24`

            MRtrix3 uses a RAS (Right-Anterior-Superior) axis convention, and internally reorients images upon loading in order to conform to this as far as possible. So for non-exotic data, axis 1 should correspond (approximately) to the anterior-posterior direction.


        Extract only every other volume from a 4D image:

            `$ mrconvert all.mif every_other.mif -coord 3 1:2:end`

            This example demonstrates two features: Use of the colon syntax to conveniently specify a number sequence (in the format 'start:step:stop'); and use of the 'end' keyword to generate this sequence up to the size of the input image along that axis (i.e. the number of volumes).


        Alter the image header to report a new isotropic voxel size:

            `$ mrconvert in.mif isotropic.mif -vox 1.25`

            By providing a single value to the -vox option only, the specified value is used to set the voxel size in mm for all three spatial axes in the output image.


        Alter the image header to report a new anisotropic voxel size:

            `$ mrconvert in.mif anisotropic.mif -vox 1,,3.5`

            This example will change the reported voxel size along the first and third axes (ideally left-right and inferior-superior) to 1.0mm and 3.5mm respectively, and leave the voxel size along the second axis (ideally anterior-posterior) unchanged.


        Turn a single-volume 4D image into a 3D image:

            `$ mrconvert 4D.mif 3D.mif -axes 0,1,2`

            Sometimes in the process of extracting or calculating a single 3D volume from a 4D image series, the size of the image reported by mrinfo will be "X x Y x Z x 1", indicating that the resulting image is in fact also 4D, it just happens to contain only one volume. This example demonstrates how to convert this into a genuine 3D image (i.e. mrinfo will report the size as "X x Y x Z".


        Insert an axis of size 1 into the image:

            `$ mrconvert XYZD.mif XYZ1D.mif -axes 0,1,2,-1,3`

            This example uses the value -1 as a flag to indicate to mrconvert where a new axis of unity size is to be inserted. In this particular example, the input image has four axes: the spatial axes X, Y and Z, and some form of data D is stored across the fourth axis (i.e. volumes). Due to insertion of a new axis, the output image is 5D: the three spatial axes (XYZ), a single volume (the size of the output image along the fourth axis will be 1), and data D will be stored as volume groups along the fifth axis of the image.


        Manually reset the data scaling parameters stored within the image header to defaults:

            `$ mrconvert with_scaling.mif without_scaling.mif -scaling 0.0,1.0`

            This command-line option alters the parameters stored within the image header that provide a linear mapping from raw intensity values stored in the image data to some other scale. Where the raw data stored in a particular voxel is I, the value within that voxel is interpreted as: value = offset + (scale x I).  To adjust this scaling, the relevant parameters must be provided as a comma-separated 2-vector of floating-point values, in the format "offset,scale" (no quotation marks). This particular example sets the offset to zero and the scale to one, which equates to no rescaling of the raw intensity data.


        References
        ----------

            Tournier, J.-D.; Smith, R. E.; Raffelt, D.; Tabbara, R.; Dhollander, T.; Pietsch, M.; Christiaens, D.; Jeurissen, B.; Yeh, C.-H. & Connelly, A. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. NeuroImage, 2019, 202, 116137


        MRtrix
        ------

            Version:3.0.4, built Sep 10 2024

            Author: J-Donald Tournier (jdtournier@gmail.com) and Robert E. Smith (robert.smith@florey.edu.au)

            Copyright: Copyright (c) 2008-2024 the MRtrix3 contributors.

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Covered Software is provided under this License on an "as is"
    basis, without warranty of any kind, either expressed, implied, or
    statutory, including, without limitation, warranties that the
    Covered Software is free of defects, merchantable, fit for a
    particular purpose or non-infringing.
    See the Mozilla Public License v. 2.0 for more details.

    For more details, see http://www.mrtrix.org/.
    """

    executable = "mrconvert"

    # Arguments
    in_file: ImageIn = shell.arg(
        argstr="",
        position=0,
        help_string="""the input image.""",
        mandatory=True,
    )
    out_file: Path = shell.arg(
        argstr="",
        position=1,
        output_file_template="out_file.mif",
        help_string="""the output image.""",
    )
    # Options for manipulating fundamental image properties Option Group
    coord: MultiInputObj[ty.Tuple[int, int]] = shell.arg(
        argstr="-coord",
        help_string="""retain data from the input image only at the coordinates specified in the selection along the specified axis. The selection argument expects a number sequence, which can also include the 'end' keyword.""",
    )
    vox: ty.List[float] = shell.arg(
        argstr="-vox",
        help_string="""change the voxel dimensions reported in the output image header""",
        sep=",",
    )
    axes: ty.List[int] = shell.arg(
        argstr="-axes",
        help_string="""specify the axes from the input image that will be used to form the output image""",
        sep=",",
    )
    scaling: ty.List[float] = shell.arg(
        argstr="-scaling",
        help_string="""specify the data scaling parameters used to rescale the intensity values""",
        sep=",",
    )
    # Options for handling JSON (JavaScript Object Notation) files Option Group
    json_import: File = shell.arg(
        argstr="-json_import",
        help_string="""import data from a JSON file into header key-value pairs""",
    )
    json_export: ty.Union[Path, bool] = shell.arg(
        default=False,
        argstr="-json_export",
        output_file_template="json_export.txt",
        help_string="""export data from an image header key-value pairs into a JSON file""",
    )
    # Options to modify generic header entries Option Group
    clear_property: MultiInputObj[str] = shell.arg(
        argstr="-clear_property",
        help_string="""remove the specified key from the image header altogether.""",
    )
    set_property: MultiInputObj[ty.Tuple[str, str]] = shell.arg(
        argstr="-set_property",
        help_string="""set the value of the specified key in the image header.""",
    )
    append_property: MultiInputObj[ty.Tuple[str, str]] = shell.arg(
        argstr="-append_property",
        help_string="""append the given value to the specified key in the image header (this adds the value specified as a new line in the header value).""",
    )
    copy_properties: ty.Any = shell.arg(
        argstr="-copy_properties",
        help_string="""clear all generic properties and replace with the properties from the image / file specified.""",
    )
    # Stride options Option Group
    strides: ty.Any = shell.arg(
        argstr="-strides",
        help_string="""specify the strides of the output data in memory; either as a comma-separated list of (signed) integers, or as a template image from which the strides shall be extracted and used. The actual strides produced will depend on whether the output image format can support it.""",
    )
    # Data type options Option Group
    datatype: str = shell.arg(
        argstr="-datatype",
        help_string="""specify output image data type. Valid choices are: float16, float16le, float16be, float32, float32le, float32be, float64, float64le, float64be, int64, uint64, int64le, uint64le, int64be, uint64be, int32, uint32, int32le, uint32le, int32be, uint32be, int16, uint16, int16le, uint16le, int16be, uint16be, cfloat16, cfloat16le, cfloat16be, cfloat32, cfloat32le, cfloat32be, cfloat64, cfloat64le, cfloat64be, int8, uint8, bit.""",
        allowed_values=[
            "float16",
            "float16",
            "float16le",
            "float16be",
            "float32",
            "float32le",
            "float32be",
            "float64",
            "float64le",
            "float64be",
            "int64",
            "uint64",
            "int64le",
            "uint64le",
            "int64be",
            "uint64be",
            "int32",
            "uint32",
            "int32le",
            "uint32le",
            "int32be",
            "uint32be",
            "int16",
            "uint16",
            "int16le",
            "uint16le",
            "int16be",
            "uint16be",
            "cfloat16",
            "cfloat16le",
            "cfloat16be",
            "cfloat32",
            "cfloat32le",
            "cfloat32be",
            "cfloat64",
            "cfloat64le",
            "cfloat64be",
            "int8",
            "uint8",
            "bit",
        ],
    )
    # DW gradient table import options Option Group
    grad: File = shell.arg(
        argstr="-grad",
        help_string="""Provide the diffusion-weighted gradient scheme used in the acquisition in a text file. This should be supplied as a 4xN text file with each line is in the format [ X Y Z b ], where [ X Y Z ] describe the direction of the applied gradient, and b gives the b-value in units of s/mm^2. If a diffusion gradient scheme is present in the input image header, the data provided with this option will be instead used.""",
    )
    fslgrad: ty.Tuple[File, File] = shell.arg(
        argstr="-fslgrad",
        help_string="""Provide the diffusion-weighted gradient scheme used in the acquisition in FSL bvecs/bvals format files. If a diffusion gradient scheme is present in the input image header, the data provided with this option will be instead used.""",
    )
    bvalue_scaling: bool = shell.arg(
        argstr="-bvalue_scaling",
        help_string="""enable or disable scaling of diffusion b-values by the square of the corresponding DW gradient norm (see Description). Valid choices are yes/no, true/false, 0/1 (default: automatic).""",
    )
    # DW gradient table export options Option Group
    export_grad_mrtrix: ty.Union[Path, bool] = shell.arg(
        default=False,
        argstr="-export_grad_mrtrix",
        output_file_template="export_grad_mrtrix.txt",
        help_string="""export the diffusion-weighted gradient table to file in MRtrix format""",
    )
    export_grad_fsl: ty.Union[ty.Tuple[Path, Path], bool] = shell.arg(
        default=False,
        argstr="-export_grad_fsl",
        output_file_template=(
            "export_grad_fsl0.txt",
            "export_grad_fsl1.txt",
        ),
        help_string="""export the diffusion-weighted gradient table to files in FSL (bvecs / bvals) format""",
    )
    # Options for importing phase-encode tables Option Group
    import_pe_table: File = shell.arg(
        argstr="-import_pe_table",
        help_string="""import a phase-encoding table from file""",
    )
    import_pe_eddy: ty.Tuple[File, File] = shell.arg(
        argstr="-import_pe_eddy",
        help_string="""import phase-encoding information from an EDDY-style config / index file pair""",
    )
    # Options for exporting phase-encode tables Option Group
    export_pe_table: ty.Union[Path, bool] = shell.arg(
        default=False,
        argstr="-export_pe_table",
        output_file_template="export_pe_table.txt",
        help_string="""export phase-encoding table to file""",
    )
    export_pe_eddy: ty.Union[ty.Tuple[Path, Path], bool] = shell.arg(
        default=False,
        argstr="-export_pe_eddy",
        output_file_template=(
            "export_pe_eddy0.txt",
            "export_pe_eddy1.txt",
        ),
        help_string="""export phase-encoding information to an EDDY-style config / index file pair""",
    )
    # Standard options
    info: bool = shell.arg(
        argstr="-info",
        help_string="""display information messages.""",
    )
    quiet: bool = shell.arg(
        argstr="-quiet",
        help_string="""do not display information messages or progress status; alternatively, this can be achieved by setting the MRTRIX_QUIET environment variable to a non-empty string.""",
    )
    debug: bool = shell.arg(
        argstr="-debug",
        help_string="""display debugging messages.""",
    )
    force: bool = shell.arg(
        argstr="-force",
        help_string="""force overwrite of output files (caution: using the same file as input and output might cause unexpected behaviour).""",
    )
    nthreads: int = shell.arg(
        argstr="-nthreads",
        help_string="""use this number of threads in multi-threaded applications (set to 0 to disable multi-threading).""",
    )
    config: MultiInputObj[ty.Tuple[str, str]] = shell.arg(
        argstr="-config",
        help_string="""temporarily set the value of an MRtrix config file entry.""",
    )
    help: bool = shell.arg(
        argstr="-help",
        help_string="""display this information page and exit.""",
    )
    version: bool = shell.arg(
        argstr="-version",
        help_string="""display version information and exit.""",
    )

    @shell.outputs
    class Outputs:

        out_file: ImageOut = shell.outarg(
            help_string="""the output image.""",
        )
        json_export: File = shell.outarg(
            help_string="""export data from an image header key-value pairs into a JSON file""",
        )
        export_grad_mrtrix: File = shell.outarg(
            help_string="""export the diffusion-weighted gradient table to file in MRtrix format""",
        )
        export_grad_fsl: ty.Tuple[File, File] = shell.outarg(
            help_string="""export the diffusion-weighted gradient table to files in FSL (bvecs / bvals) format""",
        )
        export_pe_table: File = shell.outarg(
            help_string="""export phase-encoding table to file""",
        )
        export_pe_eddy: ty.Tuple[File, File] = shell.outarg(
            help_string="""export phase-encoding information to an EDDY-style config / index file pair""",
        )
