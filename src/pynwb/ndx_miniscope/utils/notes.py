import os

import pandas as pd
from packaging import version
from pynwb.misc import AnnotationSeries

from ..utils.settings import get_miniscope_version


def read_notes(folder_path: str):
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
    if miniscope_version == version.Version("4"):
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
