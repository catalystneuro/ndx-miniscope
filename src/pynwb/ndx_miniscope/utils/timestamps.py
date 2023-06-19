import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
from natsort import natsorted
from packaging import version

from ..utils.settings import get_miniscope_version


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
    if miniscope_version == version.Version("3"):
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


def get_timestamps(
    folder_path: str,
    file_pattern: Optional[str] = "Miniscope/timeStamps.csv",
    cam_num: int = 1,
) -> np.ndarray:
    miniscope_version = get_miniscope_version(folder_path=folder_path)
    if miniscope_version == version.Version("3"):
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
    if miniscope_version == version.Version("4"):
        raise NotImplementedError("This function is not supported for Miniscope V4 format.")

    fpath = os.path.join(folder_path, "timestamp.dat")
    df = pd.read_csv(fpath, sep="\t")
    df_cam = df[df["camNum"] == cam_num]
    tt = df_cam["sysClock"].values / 1000
    tt[0] = 0
    return tt
