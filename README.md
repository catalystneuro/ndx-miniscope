# ndx-miniscope Extension for NWB

This is a Neurodata Extension (NDX) for Neurodata Without Borders (NWB) 2.0 for Miniscope acquisition data.

[![PyPI version](https://badge.fury.io/py/ndx-miniscope.svg)](https://badge.fury.io/py/ndx-miniscope)

The Miniscope acquisition software generally outputs the following files:

* msCam[##].avi
* behavCam[##].avi
* timestamp.dat
* settings_and_notes.dat

This repo provides an extension to the `Device` core NWB neurodata_type called `Miniscope` which contains fields for the data in `settings_and_notes.dat`. The following code demonstrates how to use this extension to properly convert Miniscope acquisition data into NWB by creating external links, which does not require the video data to be copied into the NWB file.

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

### Usage


```python
import os
from ndx_miniscope import read_settings, read_notes, read_miniscope_timestamps, get_starting_frames
from pynwb import NWBFile, NWBHDF5IO
from datetime import datetime
from dateutil.tz import tzlocal
from pynwb.image import ImageSeries
from natsort import natsorted
from glob import glob


data_dir = 'path/to/data_dir'

session_start_time = datetime(2017, 4, 15, 12, tzinfo=tzlocal())

nwb = NWBFile('session_description', 'identifier', session_start_time)

miniscope = read_settings(data_dir)
nwb.add_device(miniscope)

annotations = read_notes(data_dir)
if annotations is not None:
    nwb.add_acquisition(annotations)

ms_files = natsorted(glob(os.path.join(data_dir, 'msCam*.avi')))
behav_files = natsorted(glob(os.path.join(data_dir, 'behavCam*.avi')))


nwb.add_acquisition(
    ImageSeries(
        name='OnePhotonSeries',
        format='external',
        external_file=[os.path.split(x)[1] for x in ms_files],
        timestamps=read_miniscope_timestamps(data_dir),
        starting_frame=get_starting_frames(ms_files),
    )
)

nwb.add_acquisition(
    ImageSeries(
        name='behaviorCam',
        format='external',
        external_file=[os.path.split(x)[1] for x in behav_files],
        timestamps=read_miniscope_timestamps(data_dir, cam_num=2),
        starting_frame=get_starting_frames(behav_files),
    )
)


save_path = os.path.join(data_dir, 'test_out.nwb')
with NWBHDF5IO(save_path, 'w') as io:
    io.write(nwb)

# test read
with NWBHDF5IO(save_path, 'r') as io:
    nwb = io.read()
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
