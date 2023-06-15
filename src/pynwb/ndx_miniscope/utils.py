import os
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from natsort import natsorted

from pynwb import NWBFile
from pynwb.misc import AnnotationSeries

from ndx_miniscope import Miniscope


def read_miniscope_timestamps(fpath, cam_num=1):
    """Reads timestamp.dat and outputs a list of times in seconds

    Parameters
    ----------
    fpath: str
        data directory or path to timestamp.dat
    cam_num: int
        number of feed

    Returns
    -------
    numpy.ndarray list if times in seconds

    """
    if not fpath[-4:] == ".dat":
        fpath = os.path.join(fpath, "timestamp.dat")
    df = pd.read_csv(fpath, sep="\t")
    df_cam = df[df["camNum"] == cam_num]
    tt = df_cam["sysClock"].values / 1000
    tt[0] = 0
    return tt


def read_settings(fpath):
    """Reads the settings_and_notes.dat and creates a Miniscope object with leaded settings

    Parameters
    ----------
    fpath: str
        data dir or path to settings_and_notes.dat

    Returns
    -------
    ndx_miniscope.Miniscope
        with settings from settings_and_notes.dat

    """
    if not fpath[-4:] == ".dat":
        fpath = os.path.join(fpath, "settings_and_notes.dat")
    df = pd.read_csv(fpath, sep="\t").loc[0]

    return Miniscope(
        name="Miniscope",
        excitation=int(df["excitation"]),
        msCamExposure=int(df["msCamExposure"]),
    )


def read_notes(fpath):
    """Reads the notes from the settings_and_notes.dat file and creates a pynwb.misc.AnnotationSeries

    Parameters
    ----------
    fpath: str
        data dir or path to settings_and_notes.dat

    Returns
    -------
    None or pynwb.misc.AnnotationSeries

    """
    if not fpath[-4:] == ".dat":
        fpath = os.path.join(fpath, "settings_and_notes.dat")
    df = pd.read_csv(fpath, skiprows=3, delimiter="\t")
    if len(df):
        return AnnotationSeries(
            name="notes",
            data=df["Note"].values,
            timestamps=df["elapsedTime"].values / 1000,
            description="read from miniscope settings_and_notes.dat file",
        )

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


def get_starting_frames(folder_path: str) -> List[int]:
    """
    Returns the list of starting frames for the behavior movies.
    Each entry is a frame number that corresponds to the first frame of each file listed in file_paths as if they were continuous.

    Parameters
    ----------
    folder_path : str
        The folder path that points to the main Miniscope folder.
        The behavior movie files are expected to be located in subfolders (e.g. 'BehavCam 2/') within the main folder.

    """
    try:
        import cv2
    except ImportError:
        raise "To use this function install cv2: \n\n pip install opencv-python-headless\n\n"

    folder_path = Path(folder_path)
    behav_avi_file_paths = natsorted(list(folder_path.glob("*/BehavCam*/*.avi")))

    starting_frames = [0]
    for behavior_movie_file_path in behav_avi_file_paths[:-1]:
        video_capture = cv2.VideoCapture(str(behavior_movie_file_path))
        num_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        starting_frames.append(starting_frames[-1] + num_frames)

    return starting_frames


def get_timestamps(folder_path: str, file_pattern: Optional[str] = "Miniscope/timeStamps.csv") -> np.ndarray:
    folder_path = Path(folder_path)
    timestamps_file_paths = natsorted(list(Path(folder_path).rglob(file_pattern)))
    assert timestamps_file_paths, f"The Miniscope timestamps ('timeSramps.csv') are missing from '{folder_path}'."

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


def add_miniscope_device(nwbfile: NWBFile, miniscope_config: Dict) -> NWBFile:
    device_metadata = deepcopy(miniscope_config)
    assert "deviceName" in device_metadata
    device_name = device_metadata.pop("deviceName").replace(" ", "")

    if device_name in nwbfile.devices:
        return nwbfile

    device_metadata.update(name=device_name)
    device_metadata.pop("deviceDirectory", None)
    device_metadata.pop("deviceID", None)

    roi = device_metadata.pop("ROI", None)
    if roi:
        device_metadata.update(ROI=[roi["height"], roi["width"]])

    device = Miniscope(**device_metadata)
    nwbfile.add_device(device)

    return nwbfile


def read_miniscope_config(file_path: str):
    assert "metaData.json" in file_path
    with open(file_path, newline="") as f:
        miniscope_config = json.loads(f.read())

    return miniscope_config
