import os

import pandas as pd
from hdmf import docval
from hdmf.utils import get_docval, popargs
from pynwb.device import Device
from pynwb.misc import AnnotationSeries

from pynwb import register_class


@register_class("Miniscope", "ndx-miniscope")
class Miniscope(Device):
    """The extension of Device to hold metadata specific to Miniscopes."""

    __nwbfields__ = (
        "version",
        "compression",
        "deviceType",
        "frameRate",
        "framesPerFile",
        "gain",
        "led0",
        "excitation",
        "msCamExposure",
        "ROI",
    )

    @docval(
        *get_docval(
            Device.__init__,
            "name",
        ),  # required
        {
            "name": "version",
            "type": str,
            "doc": "The version of Miniscope e.g., V3, V4.",
            "default": None,
        },
        {
            "name": "compression",
            "type": str,
            "doc": "The type of Compression CODEC. GREY is no compression. FFV1 losslessly compresses.",
            "default": None,
        },
        {
            "name": "deviceType",
            "type": str,
            "doc": "A device type supported by Miniscope-DAQ Software (e.g., Miniscope_V4_BNO).",
            "default": None,
        },
        {
            "name": "frameRate",
            "type": str,
            "doc": "Frame rate (e.g., 20FPS)",
            "default": None,
        },
        {
            "name": "framesPerFile",
            "type": int,
            "doc": "The number of frames stored per file.",
            "default": None,
        },
        {
            "name": "gain",
            "type": str,
            "doc": "Gain settings corresponding to Low, Medium, High.",
            "default": None,
        },
        {
            "name": "led0",
            "type": int,
            "doc": "Excitation LED intensity (range 0 - 100).",
            "default": None,
        },
        {
            "name": "excitation",
            "type": int,
            "doc": "The magnitude of excitation.",
            "default": None,
        },
        {
            "name": "msCamExposure",
            "type": int,
            "doc": "The exposure of camera (max=255).",
            "default": None,
        },
        {
            "name": "ROI",
            "type": ("array_data", "data"),
            "doc": "The bounding box (height x width) of the portion of the video that is saved to disk. Edges are zero-indexed.",
            "default": None,
            "shape": (None,),
        },
    )
    def __init__(self, **kwargs):
        name = popargs("name", kwargs)
        super().__init__(name=name)
        for config_name, config_value in kwargs.items():
            setattr(self, config_name, config_value)


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


def get_starting_frames(video_files):
    import cv2

    out = [0]
    for video_file in video_files[:-1]:
        cap = cv2.VideoCapture(video_file)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        out.append(length)

    return out
