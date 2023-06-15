import os
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from hdmf.backends.hdf5 import H5DataIO
from natsort import natsorted
from packaging import version

from pynwb import NWBFile
from pynwb.image import ImageSeries
from pynwb.misc import AnnotationSeries

from ndx_miniscope import Miniscope


def read_miniscope_timestamps(folder_path: str, cam_num=1):
    """Reads timestamp.dat and outputs a list of times in seconds

    Parameters
    ----------
    folder_path: str: str
        The folder path that points to the main Miniscope folder.
    cam_num: int
        number of feed

    Returns
    -------
    numpy.ndarray list of times in seconds

    """
    miniscope_version = get_miniscope_version(folder_path=folder_path)
    if miniscope_version == version.Version("v4"):
        raise NotImplementedError("This function is not supported for Miniscope V4 format.")

    fpath = os.path.join(folder_path, "timestamp.dat")
    df = pd.read_csv(fpath, sep="\t")
    df_cam = df[df["camNum"] == cam_num]
    tt = df_cam["sysClock"].values / 1000
    tt[0] = 0
    return tt


def read_settings(folder_path):
    """Reads the settings_and_notes.dat and creates a Miniscope object with leaded settings

    Parameters
    ----------
    folder_path: str
        data dir containing settings_and_notes.dat

    Returns
    -------
    ndx_miniscope.Miniscope
        with settings from settings_and_notes.dat

    """
    miniscope_version = get_miniscope_version(folder_path=folder_path)
    if miniscope_version == version.Version("v4"):
        raise NotImplementedError("This function is not supported for Miniscope V4 format.")

    fpath = os.path.join(folder_path, "settings_and_notes.dat")
    df = pd.read_csv(fpath, sep="\t").loc[0]

    return Miniscope(
        name="Miniscope",
        excitation=int(df["excitation"]),
        msCamExposure=int(df["msCamExposure"]),
    )


def read_notes(folder_path):
    """Reads the notes from the settings_and_notes.dat file and creates a pynwb.misc.AnnotationSeries

    Parameters
    ----------
    folder_path: str
        data dir containing settings_and_notes.dat

    Returns
    -------
    None or pynwb.misc.AnnotationSeries

    """
    miniscope_version = get_miniscope_version(folder_path=folder_path)
    if miniscope_version == version.Version("v4"):
        raise NotImplementedError("This function is not supported for Miniscope V4 format.")

    fpath = os.path.join(folder_path, "settings_and_notes.dat")
    df = pd.read_csv(fpath, skiprows=3, delimiter="\t")
    if len(df):
        return AnnotationSeries(
            name="notes",
            data=df["Note"].values,
            timestamps=df["elapsedTime"].values / 1000,
            description="read from miniscope settings_and_notes.dat file",
        )


def get_miniscope_version(folder_path: str) -> version.Version:
    """
    Returns the version of the Miniscope based on the configuration files.

    The latest Miniscope software creates user configuration files in JSON format.
    https://github.com/Aharoni-Lab/Miniscope-DAQ-QT-Software/wiki/User-Configuration-Files

    The legacy software used to create a 'settings_and_notes.dat' file.
    http://miniscope.org/index.php/Data_Acquisition_Software

    Parameters
    ----------
    folder_path : str
        The folder path that points to the main Miniscope folder.
        The configuration files are expected to be located in subfolders within the main folder.

    Returns
    -------
    version.Version
        The version of the Miniscope based on the configuration files.
        Returns a version object 'v4' for the latest software,
        'v3' for the legacy software, or raises a NotImplementedError
        if the version cannot be determined.

    """
    folder_path = Path(folder_path)

    config_files = list(folder_path.rglob("*.json"))
    if config_files:
        return version.Version("v4")

    legacy_config_files = list(folder_path.rglob("*.dat"))
    if legacy_config_files:
        return version.Version("v3")

    raise NotImplementedError("Could not determine the version of the Miniscope.")


def read_v4_miniscope_config(file_path: str):
    assert "metaData.json" in file_path
    with open(file_path, newline="") as f:
        miniscope_config = json.loads(f.read())
    assert "deviceName" in miniscope_config, "'deviceName' field is missing from the configuration file."
    device_name = miniscope_config.pop("deviceName").replace(" ", "")
    miniscope_config.update(name=device_name)
    miniscope_config.pop("deviceDirectory", None)
    miniscope_config.pop("deviceID", None)

    return miniscope_config


def get_recording_start_times(folder_path: str) -> List[datetime]:
    """
    Returns the list of recording start times from the 'metaData.json' configuration files.

    Parameters
    ----------
    folder_path : str
        The folder path that points to the main Miniscope folder.
        The configuration files are expected to be located in subfolders within the main folder.
        The configuration file should contain 'recordingStartTime' field that corresponds
        to the start time of the Miniscope recordings.

    """
    miniscope_version = get_miniscope_version(folder_path=folder_path)
    if miniscope_version == version.Version("v3"):
        raise NotImplementedError("This function is not supported for Miniscope V3 format.")

    folder_path = Path(folder_path)
    configuration_file_name = "metaData.json"
    miniscope_config_files = natsorted(list(folder_path.glob(f"*/{configuration_file_name}")))
    assert (
        miniscope_config_files
    ), f"The configuration files ('{configuration_file_name}') are missing from '{folder_path}'."

    recording_start_times = []
    for config_file_path in miniscope_config_files:
        with open(config_file_path, newline="") as f:
            config = json.loads(f.read())

        assert "recordingStartTime" in config, "The configuration file should contain 'recordingStartTime'."
        start_time = config["recordingStartTime"]

        recording_start_times.append(
            datetime(
                year=start_time["year"],
                month=start_time["month"],
                day=start_time["day"],
                hour=start_time["hour"],
                minute=start_time["minute"],
                second=start_time["second"],
                microsecond=start_time["msec"],
            )
        )
    return recording_start_times


def get_starting_frames(folder_path: str, video_file_pattern: str = "*/BehavCam*/*.avi") -> List[int]:
    """
    Returns the list of starting frames for the behavior movies.
    Each entry is a frame number that corresponds to the first frame of each file listed in file_paths as if they were continuous.

    Parameters
    ----------
    folder_path : str
        The folder path that points to the main Miniscope folder.
        The behavior movie files are expected to be located in subfolders (e.g. 'BehavCam 2/') within the main folder.
    video_file_pattern: str, optional
        The file pattern to look for in the folder.
    """
    try:
        import cv2
    except ImportError:
        raise "To use this function install cv2: \n\n pip install opencv-python-headless\n\n"

    folder_path = Path(folder_path)
    behavior_video_file_paths = natsorted(list(folder_path.glob(video_file_pattern)))
    assert behavior_video_file_paths, f"Could not find the video files in '{folder_path}'."

    starting_frames = [0]
    for video_file_path in behavior_video_file_paths[:-1]:
        video_capture = cv2.VideoCapture(str(video_file_path))
        num_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        starting_frames.append(starting_frames[-1] + num_frames)

    return starting_frames


def get_timestamps(
        folder_path: str,
        file_pattern: Optional[str] = "Miniscope/timeStamps.csv",
        cam_num: int = 1,
) -> np.ndarray:

    miniscope_version = get_miniscope_version(folder_path=folder_path)
    if miniscope_version == version.Version("v3"):
        return read_miniscope_timestamps(folder_path=folder_path, cam_num=cam_num)

    timestamps_file_paths = natsorted(list(Path(folder_path).rglob(file_pattern)))
    assert timestamps_file_paths, f"The Miniscope timestamps are missing from '{folder_path}'."

    recording_start_times = get_recording_start_times(folder_path=str(folder_path))
    timestamps = []
    for file_ind, file_path in enumerate(timestamps_file_paths):
        timestamps_per_file = pd.read_csv(file_path)["Time Stamp (ms)"].values.astype(float)
        timestamps_per_file /= 1000
        # shift when the first timestamp is negative
        if timestamps_per_file[0] < 0.0:
            timestamps_per_file += abs(timestamps_per_file[0])

        if recording_start_times:
            offset = (recording_start_times[file_ind] - recording_start_times[0]).total_seconds()
            timestamps_per_file += offset

        timestamps.extend(timestamps_per_file)

    return np.array(timestamps)


def add_miniscope_device(nwbfile: NWBFile, device_metadata: Dict) -> NWBFile:
    device_metadata_copy = deepcopy(device_metadata)
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
    Add an ImageSeries with a linked Device based on provided metadata.
    The metadata concerning the device to be linked should be stored in metadata["Behavior]["Device"].

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
    assert "ImageSeries" in metadata["Behavior"], "The metadata for ImageSeries should be stored in metadata['Behavior']['ImageSeries']."
    assert "Device" in metadata["Behavior"], "The metadata for Device should be stored in metadata['Behavior']['Device']."
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
    assert len(starting_frames) == len(external_files), "The number of external files must match the length of 'starting_frame'."
    image_series_kwargs.update(
        format="external",
        external_file=external_files,
        starting_frame=starting_frames,
        timestamps=H5DataIO(timestamps, compression=True),
    )

    image_series = ImageSeries(**image_series_kwargs)
    nwbfile.add_acquisition(image_series)
