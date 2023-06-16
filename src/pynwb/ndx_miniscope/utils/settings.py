import json
import os
from pathlib import Path
from typing import Dict

import pandas as pd
from packaging import version


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
        The folder path to the main Miniscope folder that contains the configuration files.

    Returns
    -------
    version.Version
        The version of the Miniscope based on the configuration files.
        Returns a version object '4' for the latest software,
        '3' for the legacy software, or raises a NotImplementedError
        if the version cannot be determined.

    """
    folder_path = Path(folder_path)

    config_files = list(folder_path.rglob("*.json"))
    if config_files:
        return version.Version("4")

    legacy_config_files = list(folder_path.rglob("*.dat"))
    if legacy_config_files:
        return version.Version("3")

    raise NotImplementedError("Could not determine the version of the Miniscope.")


def read_miniscope_config(folder_path: str) -> Dict:
    """
    Loads the configuration file as dictionary object from the main Miniscope folder.

    The latest Miniscope software creates user configuration files in JSON format.
    https://github.com/Aharoni-Lab/Miniscope-DAQ-QT-Software/wiki/User-Configuration-Files

    The legacy software used to create a 'settings_and_notes.dat' file.
    http://miniscope.org/index.php/Data_Acquisition_Software

    settings_and_notes.dat and creates a Miniscope object with leaded settings

    Parameters
    ----------
    folder_path: str
        The folder path where the settings of the microscope or the behavioral camera is located.


    Returns
    -------
    Dict
        The dictionary with the Miniscope settings.

    """
    miniscope_version = get_miniscope_version(folder_path=folder_path)
    if miniscope_version == version.Version("3"):
        return read_v3_miniscope_config(folder_path=folder_path)

    return read_v4_miniscope_config(folder_path=folder_path)


def read_v3_miniscope_config(folder_path: str):
    fpath = os.path.join(folder_path, "settings_and_notes.dat")
    df = pd.read_csv(fpath, sep="\t").loc[0]

    return dict(
        name="Miniscope",
        excitation=int(df["excitation"]),
        msCamExposure=int(df["msCamExposure"]),
    )


def read_v4_miniscope_config(folder_path: str) -> Dict:
    file_path = os.path.join(folder_path, "metaData.json")
    with open(file_path, newline="") as f:
        miniscope_config = json.loads(f.read())
    assert "deviceName" in miniscope_config, "'deviceName' field is missing from the configuration file."
    device_name = miniscope_config.pop("deviceName").replace(" ", "")
    miniscope_config.update(name=device_name)
    miniscope_config.pop("deviceDirectory", None)
    miniscope_config.pop("deviceID", None)

    return miniscope_config

