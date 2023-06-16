from copy import deepcopy
from typing import Dict, Optional, List

import numpy as np
from hdmf.backends.hdf5 import H5DataIO
from pynwb import NWBFile
from pynwb.image import ImageSeries

from ndx_miniscope import Miniscope


def add_miniscope_device(nwbfile: NWBFile, device_metadata: Dict) -> NWBFile:
    """
    Adds a Miniscope device based on provided metadata.
    Can be used to add device for the microscope and the behavioral camera.

    Parameters
    ----------
    nwbfile : NWBFile
        The nwbfile to add the Miniscope device to.
    device_metadata: Dict
        The metadata for the device to be added.

    Returns
    -------
    NWBFile
        The NWBFile passed as an input with the Miniscope added.

    """
    device_metadata_copy = deepcopy(device_metadata)
    assert "name" in device_metadata_copy, "'name' is missing from metadata."
    device_name = device_metadata_copy["name"]
    if device_name in nwbfile.devices:
        return nwbfile

    roi = device_metadata_copy.pop("ROI", None)
    if roi:
        device_metadata_copy.update(ROI=[roi["height"], roi["width"]])

    device = Miniscope(**device_metadata_copy)
    nwbfile.add_device(device)

    return nwbfile


def add_miniscope_image_series(
    nwbfile: NWBFile,
    metadata: Dict,
    timestamps: np.ndarray,
    image_series_index: int = 0,
    external_files: Optional[List[str]] = None,
    starting_frames: Optional[List[int]] = None,
) -> NWBFile:
    """
    Adds an ImageSeries with a linked Miniscope device based on provided metadata.
    The metadata for the device to be linked should be stored in metadata["Behavior]["Device"].

    Parameters
    ----------
    nwbfile : NWBFile
        The nwbfile to add the image series to.
    metadata: DeepDict
        The metadata storing the necessary metadata for creating the image series and linking it to the appropriate device.
    timestamps : np.ndarray
        The timestamps for the behavior movie source.
    image_series_index : int, optional
        The metadata for ImageSeries is a list of the different image series to add.
        Specify which element of the list with this parameter.
    external_files : List[str], optional
        List of external files associated with the ImageSeries.
    starting_frames :  List[int], optional
        List of starting frames for each external file.

    Returns
    -------
    NWBFile
        The NWBFile passed as an input with the ImageSeries added.

    """
    assert "Behavior" in metadata, "The metadata for ImageSeries and Device should be stored in 'Behavior'."
    assert (
        "ImageSeries" in metadata["Behavior"]
    ), "The metadata for ImageSeries should be stored in metadata['Behavior']['ImageSeries']."
    assert (
        "Device" in metadata["Behavior"]
    ), "The metadata for Device should be stored in metadata['Behavior']['Device']."
    image_series_kwargs = deepcopy(metadata["Behavior"]["ImageSeries"][image_series_index])
    image_series_name = image_series_kwargs["name"]

    if image_series_name in nwbfile.acquisition:
        return nwbfile

    # Add linked device to ImageSeries
    device_metadata = metadata["Behavior"]["Device"][image_series_index]
    device_name = device_metadata["name"]
    if device_name not in nwbfile.devices:
        add_miniscope_device(nwbfile=nwbfile, device_metadata=device_metadata)
    device = nwbfile.get_device(name=device_name)
    image_series_kwargs.update(device=device)

    assert external_files, "'external_files' must be specified."
    if starting_frames is None and len(external_files) == 1:
        starting_frames = [0]
    assert len(starting_frames) == len(
        external_files
    ), "The number of external files must match the length of 'starting_frame'."
    image_series_kwargs.update(
        format="external",
        external_file=external_files,
        starting_frame=starting_frames,
        timestamps=H5DataIO(timestamps, compression=True),
    )

    image_series = ImageSeries(**image_series_kwargs)
    nwbfile.add_acquisition(image_series)
