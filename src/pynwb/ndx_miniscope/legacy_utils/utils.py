import os

import pandas as pd
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
