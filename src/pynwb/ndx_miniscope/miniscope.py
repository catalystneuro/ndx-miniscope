import json
import os
from glob import glob
from warnings import warn

import pandas as pd
from natsort import natsorted
from numpy import ndarray
from pynwb.image import ImageSeries
from pynwb.misc import AnnotationSeries

from pynwb import NWBFile, get_class, load_namespaces

name = "ndx-miniscope"

here = os.path.abspath(os.path.dirname(__file__))
ns_path = os.path.join(here, "spec", name + ".namespace.yaml")

load_namespaces(ns_path)

Miniscope = get_class("Miniscope", name)


class MiniscopeLoader:
    """Load Miniscope V3 or V4 metadata for generating NWB files

    Parameters
    ----------
    fpath: str
        data dir or path to settings_and_notes.dat
    version: str, default V3
        miniscope version. V3 and V4 currently supported
    """

    def __init__(self, fpath: str, version: str = "V3") -> None:
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Could not find local path {fpath}")
        if version not in ["V3", "V4"]:
            raise NotImplementedError("This module only supports Miniscope V3 and V4")

        self._fpath = fpath
        self._version = version

    def _to_seconds(self, values: ndarray) -> ndarray:
        """Return values / 1000, replacing first item with zero"""
        output = values / 1000
        output[0] = 0
        return output

    def read_miniscope_timestamps(self, cam_num: int = 1) -> ndarray:
        """Reads timestamp dat or csv and outputs a list of times in seconds

        Parameters
        ----------
        cam_num: int, default 1
            number of feed

        Returns
        -------
        numpy.ndarray list if times in seconds

        """
        if self._version == "V3":
            fpath = os.path.join(self._fpath, "timestamp.dat")
            df = pd.read_csv(fpath, sep="\t")
            df_cam = df[df["camNum"] == cam_num]
            tt_msec = df_cam["sysClock"].values
        elif self._version == "V4":
            fpath = os.path.join(self._fpath, "timestamps.csv")
            df = pd.read_csv(fpath, sep="\t")
            tt_msec = df["Time Stamp (ms)"].values

        return self._to_seconds(tt_msec)

    def read_settings(self, excitation: int = None, msCamExposure: int = None, **kwargs) -> Miniscope:
        """Creates a Miniscope object with leaded settings

        For V3, reads settings_and_notes.dat. For V4, supply excitation and
        msCamExposure manually as function parameters.

        Parameters
        ----------
        excitation: int, optional
            V4: manually provide this value. V3: read from settings_and_notes.dat.
        msCamExposure: int, optional
            V4: manually provide this value. V3: read from settings_and_notes.dat.
        kwargs: dict
            Any additional keyword arguments outlined in the Miniscope device extension.

        Returns
        -------
        ndx_miniscope.Miniscope
            with excitation and msCamExposure values

        """
        miniscope_fields = [field["name"] for field in Miniscope.get_fields_conf()]
        settings_dict = dict(
            name="Miniscope",
            **{k: v for k, v in kwargs.items() if k in miniscope_fields},
        )

        if self._version == "V3":
            fpath = os.path.join(self._fpath, "settings_and_notes.dat")
            df = pd.read_csv(fpath, sep="\t").loc[0]
            excitation = excitation or int(df["excitation"])
            msCamExposure = msCamExposure or int(df["msCamExposure"])

        if self._version == "V4" and not any([excitation, msCamExposure]):
            warn(
                "Miniscope V4 settings do not predictably store excitation or camera "
                + "exposure. If available, please supply these values when calling the "
                + "MiniscopeLoader.read_settings function.",
                stacklevel=2,
            )

        if self._version == "V4":
            fpath = os.path.join(self._fpath, "metaData.json")
            with open(fpath, newline="") as f:
                read_metadata = json.loads(f.read())
            read_metadata["name"] = read_metadata.pop("deviceName")
            read_metadata.pop("deviceDirectory", None)  # Local absolute path
            read_metadata.pop("deviceID", None)  # Int of devices attached to computer

            if "ROI" in read_metadata:  # Is there a better way to pass this as dict?
                read_metadata["ROI"] = list(read_metadata["ROI"].values())
            # CustomClassGenerator wouldn't accept gain as int. possible values: 2, 2.5
            if isinstance(read_metadata.get("gain"), int):
                read_metadata["gain"] = float(read_metadata["gain"])
            for field in read_metadata:
                removed_items = []
                if field not in miniscope_fields:
                    removed_items.append(read_metadata.pop(field))
            if removed_items:
                warn(
                    "The following are not yet part of the ndx-miniscope spec:"
                    + f"{removed_items}\nConsider supporting development at "
                    + "https://github.com/catalystneuro/ndx-miniscope"
                )

            settings_dict.update(read_metadata)

        return Miniscope(
            **settings_dict,
            version=self._version,
            excitation=excitation,
            msCamExposure=msCamExposure,
        )

    def read_notes(self, notes_filename=""):
        """Reads the notes and creates a pynwb.misc.AnnotationSeries

        For V3, reads notes from the settings_and_notes.dat. For V4,

        Parameters
        ----------
        fpath: str
            data dir or path to settings_and_notes.dat

        Returns
        -------
        None or pynwb.misc.AnnotationSeries
        """
        if self._version == "V3":
            fpath = os.path.join(self._fpath, "settings_and_notes.dat")
            df = pd.read_csv(fpath, skiprows=3, delimiter="\t")
            if not len(df):
                return
            name = "Notes"
            data = df["Note"].values
            timestamps = df["elapsedTime"].values / 1000
            description = "Read from Miniscope settings_and_notes.dat file"

        elif self._version == "V4":
            fpaths = [
                path
                for path in glob(os.path.join(self._fpath, "*.csv"))
                if "timeStamps" not in path and notes_filename in path
            ]
            if len(fpaths) != 1:
                raise FileNotFoundError(
                    f"Found {len(fpaths)} possible notes file(s). Try specifying the "
                    + "filename when calling MiniscopeLoader.read_notes to identify one"
                    + f"file.\n{fpaths}"
                )
            df = pd.read_csv(fpaths[0], delimiter=",")
            if not len(df):
                return
            name = os.path.basename(fpaths[0]).split(".")[0]  # file stem
            timestamps = self._to_seconds(df["Time Stamp (ms)"].values)
            description = f"Read from Miniscope {name}.csv file"

            # TODO: I don't know how many dimensions this will have.
            # Example headOrientation data has 4 float columns - Quaternion data
            # https://groups.google.com/g/miniscope/c/ISGU88Z6JKI
            # Documentation suggests other Notes files may be present
            # https://github.com/Aharoni-Lab/Miniscope-DAQ-QT-Software/blob/master/source/datasaver.cpp#L345
            data = None

            raise NotImplementedError("The portion of the V4 export is not yet complete.")

        return AnnotationSeries(
            name=name,
            data=data,
            timestamps=timestamps,
            description=description,
        )

    def _get_starting_frames(self, video_files):
        import cv2

        out = [0]
        for video_file in video_files[:-1]:
            cap = cv2.VideoCapture(video_file)
            length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            out.append(length)

        return out

    def external_image_series(self, name="OnePhotonSeries", file_pattern="*.avi"):
        """Return an NWB external ImageSeries for the files according to file_pattern

        Parameters
        ----------
        name: str, default OnePhotonSeries
            Image series name. e.g., OnePhotonSeries, behaviorCam
        file_pattern: str, default *.avi
            Pattern for files to include in ImageSeries, accepting wild cards

        Returns
        -------
        pynwb.image.ImageSeries
        """
        files = natsorted(glob(os.path.join(self._fpath, file_pattern)))
        if not files:
            raise FileNotFoundError(f"Could not find any files matching {file_pattern} in {self._fpath}")
        return ImageSeries(
            name=name,
            format="external",
            external_file=[os.path.split(x)[1] for x in files],
            timestamps=self.read_miniscope_timestamps(),
            starting_frame=self._get_starting_frames(files),
        )
