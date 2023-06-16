# ndx-miniscope Extension for NWB

This is a Neurodata Extension (NDX) for Neurodata Without Borders (NWB) 2.0 for Miniscope acquisition data.

[![PyPI version](https://badge.fury.io/py/ndx-miniscope.svg)](https://badge.fury.io/py/ndx-miniscope)

`Miniscope` extends the `Device` core NWB neurodata_type by including additional metadata for the Miniscope.
Depending on the version of the acquisition software the data structure can be quite different.

## Miniscope V4 format
The data recorded by the software is saved in a folder structure similar to this:

* `C6-J588_Disc5/` (main folder)
   * `15_03_28/` (subfolder corresponding to the recording time)
        * `Miniscope/` (subfolder containing the microscope video stream)
            * `0.avi` (file containing the microscope video)
            * `metaData.json` (file containing the metadata for the microscope device)
            * `timeStamps.csv` (file containing the timing of this video stream)
        * `BehavCam_2/` (subfolder containing the behavioral video stream)
            * `0.avi` (file containing the bevavioral video)
            * `metaData.json` (file containing the metadata for the behavioral camera)
            * `timeStamps.csv` (file containing the timing of this video stream)
        * `metaData.json` (file containing metadata for the recording, such as the start time)
   * `15_06_28/` (another subfolder)
        * `Miniscope/`
        * `BehavCam_2/`
        * `metaData.json`

## Miniscope V3 format
The Miniscope V3 acquisition software generally outputs the following files:

* msCam[##].avi
* behavCam[##].avi
* timestamp.dat
* settings_and_notes.dat


## python
### Installation

Get most recent release:
```bash
pip install ndx-miniscope
```

Install latest:
```bash
git clone https://github.com/catalystneuro/ndx-miniscope.git
cd ndx-miniscope
pip install -e .
```

The following code demonstrates the usage of this extension to convert Miniscope acquisition data into NWB.

### Usage

```python
from datetime import datetime
from dateutil.tz import tzlocal
import glob
import os
from pynwb import NWBFile, NWBHDF5IO
from pynwb.image import ImageSeries
from natsort import natsorted

from ndx_miniscope.utils import (
    add_miniscope_device,
    get_starting_frames,
    get_timestamps,
    read_miniscope_config,
    read_notes,
)

# The main folder that contains subfolders with the Miniscope data
folder_path = "C6-J588_Disc5/"

# Create the NWBFile
session_start_time = datetime(2017, 4, 15, 12, tzinfo=tzlocal())
nwbfile = NWBFile(
    session_description="session_description",
    identifier="identifier",
    session_start_time=session_start_time,
)

# Load the miscroscope settings
miniscope_folder_path = "C6-J588_Disc5/15_03_28/Miniscope/"
miniscope_metadata = read_miniscope_config(folder_path=miniscope_folder_path)
# Create the Miniscope device with the microscope metadata and add it to NWB
add_miniscope_device(nwbfile=nwbfile, device_metadata=miniscope_metadata)

# Load the behavioral camera settings
behavcam_folder_path = "C6-J588_Disc5/15_03_28/BehavCam_2/"
behavcam_metadata = read_miniscope_config(folder_path=behavcam_folder_path)
# Create the Miniscope device with the behavioral camera metadata and add it to NWB
add_miniscope_device(nwbfile=nwbfile, device_metadata=behavcam_metadata)

# Loading the timestamps
behavcam_timestamps = get_timestamps(folder_path=folder_path, file_pattern="BehavCam*/timeStamps.csv")
# Load the starting frames of the video files
# Note this function requires to have `cv2` installed
starting_frames = get_starting_frames(folder_path=folder_path, video_file_pattern="*/BehavCam*/*.avi")

# TODO: redirect to MiniscopeConverter

# Legacy usage for Miniscope V3

ms_files = natsorted(glob(os.path.join(folder_path, 'msCam*.avi')))
nwbfile.add_acquisition(
    ImageSeries(
        name='OnePhotonSeries',  # this is not recommended since pynwb has native OnePhotonSeries
        format='external',
        external_file=[os.path.split(x)[1] for x in ms_files],
        timestamps=get_timestamps(folder_path=folder_path, cam_num=1),
        starting_frame=get_starting_frames(folder_path=folder_path, video_file_pattern="msCam*.avi"),
    )
)

behav_files = natsorted(glob(os.path.join(folder_path, 'behavCam*.avi')))
nwbfile.add_acquisition(
    ImageSeries(
        name='behaviorCam',
        format='external',
        external_file=[os.path.split(x)[1] for x in behav_files],
        timestamps=get_timestamps(folder_path=folder_path, cam_num=2),
        starting_frame=get_starting_frames(folder_path=folder_path, video_file_pattern="behavCam*.avi"),
    )
)

annotations = read_notes(folder_path=folder_path)
if annotations is not None:
    nwbfile.add_acquisition(annotations)


save_path = os.path.join(folder_path, "test_out.nwb")
with NWBHDF5IO(save_path, "w") as io:
    io.write(nwbfile)

# test read
with NWBHDF5IO(save_path, "r") as io:
    nwbfile_in = io.read()

```


## MATLAB:
### Installation
```bash
git clone https://github.com/bendichter/ndx-miniscope.git
```
```matlab
generateExtension('path/to/ndx-miniscope/spec');
```

### Usage
under construction...
