# ndx-miniscope Extension for NWB

This is a Neurodata Extension (NDX) for Neurodata Without Borders (NWB) 2.0 for Miniscope acquisition data.

[![PyPI version](https://badge.fury.io/py/ndx-miniscope.svg)](https://badge.fury.io/py/ndx-miniscope)

`Miniscope` extends the `Device` core NWB neurodata_type by including additional metadata for the Miniscope.
Depending on the version of the acquisition software the data structure can be quite different.

## Miniscope V4 format
The data recorded by the software is saved in a folder structure similar to this:

        C6-J588_Disc5/ (main folder)
        ├── 15_03_28/ (subfolder corresponding to the recording time)
        │   ├── Miniscope/ (subfolder containing the microscope video stream)
        │   │   ├── 0.avi (microscope video)
        │   │   ├── metaData.json (metadata for the microscope device)
        │   │   └── timeStamps.csv (timing of this video stream)
        │   ├── BehavCam_2/ (subfolder containing the behavioral video stream)
        │   │   ├── 0.avi (bevavioral video)
        │   │   ├── metaData.json (metadata for the behavioral camera)
        │   │   └── timeStamps.csv (timing of this video stream)
        │   └── metaData.json (metadata for the recording, such as the start time)
        ├── 15_06_28/
        │   ├── Miniscope/
        │   ├── BehavCam_2/
        │   └── metaData.json
        └── 15_12_28/

## Miniscope V3 format
The Miniscope V3 acquisition software generally outputs the following files:

* msCam[##].avi
* behavCam[##].avi
* timestamp.dat
* settings_and_notes.dat


## python

### Convert to NWB using NeuroConv

Use the `MiniscopeConverter` from NeuroConv to easily convert Miniscope acquisition data to NWB.

Install NeuroConv with the additional dependencies necessary for reading Miniscope data.
```bash
pip install neuroconv[miniscope]
```

The `MiniscopeConverter` combines the imaging and behavior data streams into a single conversion.

```jupyterpython
from dateutil import tz
from neuroconv.converters import MiniscopeConverter

# The 'folder_path' is the path to the main Miniscope folder containing both the recording and behavioral data streams in separate subfolders.
folder_path = "C6-J588_Disc5/"
converter = MiniscopeConverter(folder_path=folder_path, verbose=False)

metadata = converter.get_metadata()
# For data provenance we can add the time zone information to the conversion if missing
session_start_time = metadata["NWBFile"]["session_start_time"]
tzinfo = tz.gettz("US/Pacific")
metadata["NWBFile"].update(session_start_time=session_start_time.replace(tzinfo=tzinfo))

# Choose a path for saving the nwb file and run the conversion
nwbfile_path = "miniscope.nwb"
converter.run_conversion(nwbfile_path=nwbfile_path, metadata=metadata)
```
### Access the data from NWB

Access the `Miniscope` devices from the in-memory `NWBFile`.
```jupyterpython
from pynwb import NWBHDF5IO

nwbfile_path = "miniscope.nwb"
with NWBHDF5IO(nwbfile_path, "r") as io:
    nwbfile_in = io.read()
    # Access the device with the microscope metadata
    nwbfile_in.devices["Miniscope"]
    # Access the device that holds the metadata for the behavior camera
    nwbfile_in.devices["BehavCam2"]
```
```jupyter
Miniscope abc.Miniscope at 0x5775754960
Fields:
  compression: FFV1
  deviceType: Miniscope_V3
  frameRate: 15FPS
  framesPerFile: 1000
  gain: High
  led0: 47

BehavCam2 abc.Miniscope at 0x5775972816
Fields:
  ROI: <HDF5 dataset "ROI": shape (2,), type "<i8">
  compression: MJPG
  deviceType: WebCam-1920x1080
  framesPerFile: 1000
```
The imaging data was added to the `NWBFile` as `OnePhotonSeries` which can be accessed
from the file as the follows:
```jupyterpython
from pynwb import NWBHDF5IO

nwbfile_path = "miniscope.nwb"
with NWBHDF5IO(nwbfile_path, "r") as io:
    nwbfile_in = io.read()
    # Access the OnePhotonSeries that holds the imaging data from the microscope.
    nwbfile.acquisition["OnePhotonSeries"]
```
```jupyter
OnePhotonSeries pynwb.ophys.OnePhotonSeries at 0x5775755728
Fields:
  comments: no comments
  conversion: 1.0
  data: <HDF5 dataset "data": shape (100, 752, 480), type "|u1">
  description: Imaging data from one-photon excitation microscopy.
  dimension: <HDF5 dataset "dimension": shape (2,), type "<i8">
  imaging_plane: ImagingPlane pynwb.ophys.ImagingPlane at 0x5775755200
Fields:
  conversion: 1.0
  description: The plane or volume being imaged by the microscope.
  device: Miniscope abc.Miniscope at 0x5775754960
Fields:
  compression: FFV1
  deviceType: Miniscope_V3
  frameRate: 15FPS
  framesPerFile: 1000
  gain: High
  led0: 47
  excitation_lambda: nan
  imaging_rate: 15.0
  indicator: unknown
  location: unknown
  optical_channel: (
    OpticalChannel <class 'pynwb.ophys.OpticalChannel'>
  )
  unit: meters
  interval: 1
  offset: 0.0
  resolution: -1.0
  timestamps: <HDF5 dataset "timestamps": shape (100,), type "<f8">
  timestamps_unit: seconds
  unit: px
```
The behavior camera data was added to the `NWBFile` as `ImageSeries` which can be accessed
from the file as the follows:
```jupyterpython
from pynwb import NWBHDF5IO

nwbfile_path = "miniscope.nwb"
with NWBHDF5IO(nwbfile_path, "r") as io:
    nwbfile_in = io.read()
    # Access the ImageSeries that holds the behavior data.
    nwbfile.acquisition["BehavCamImageSeries"]
```
```jupyter
BehavCamImageSeries pynwb.image.ImageSeries at 0x5775971616
Fields:
  comments: no comments
  conversion: 1.0
  data: <HDF5 dataset "data": shape (0, 0, 0), type "|u1">
  description: no description
  device: BehavCam2 abc.Miniscope at 0x5775972816
Fields:
  ROI: <HDF5 dataset "ROI": shape (2,), type "<i8">
  compression: MJPG
  deviceType: WebCam-1920x1080
  framesPerFile: 1000
  dimension: <HDF5 dataset "dimension": shape (2,), type "<i8">
  external_file: <StrDataset for HDF5 dataset "external_file": shape (5,), type "|O">
  format: external
  interval: 1
  offset: 0.0
  resolution: -1.0
  starting_frame: [   0  690 1383 2073 2763]
  timestamps: <HDF5 dataset "timestamps": shape (3453,), type "<f8">
  timestamps_unit: seconds
  unit: px
```

For more information about accessing data in NWB, visit the [File Basics tutorial](https://pynwb.readthedocs.io/en/stable/tutorials/general/file.html).
To learn more about NeuroConv, visit this [documentation page](https://neuroconv.readthedocs.io/en/main/index.html).



### Installing `ndx-miniscope`

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
