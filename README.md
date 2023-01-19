# ndx-miniscope Extension for NWB

This is a Neurodata Extension (NDX) for Neurodata Without Borders (NWB) 2.0 for Miniscope acquisition data.

[![PyPI version](https://badge.fury.io/py/ndx-miniscope.svg)](https://badge.fury.io/py/ndx-miniscope)

The Miniscope V3 acquisition software generally outputs the following files:

* msCam[##].avi
* behavCam[##].avi
* timestamp.dat
* settings_and_notes.dat

The Miniscope V4 acquisition software generally outputs the following files:

* [#].avi
* {notes,headOrientation}.csv
* metaData.json
* timestamps.csv

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
from ndx_miniscope import MiniscopeLoader
from pynwb import NWBFile, NWBHDF5IO
from datetime import datetime
from dateutil.tz import tzlocal


data_dir = "path/to/data_dir"

session_start_time = datetime(2017, 4, 15, 12, tzinfo=tzlocal())

nwb = NWBFile("session_description", "identifier", session_start_time)

miniscope_loader = MiniscopeLoader(data_dir, version="V3")
nwb.add_device(miniscope_loader.read_settings())

annotations = miniscope_loader.read_notes()
if annotations is not None:
    nwb.add_acquisition(annotations)

nwb.add_acquisition(
    miniscope_loader.external_image_series(
        name="OnePhotonSeries",
        file_pattern="msCam*avi",
    )
)
nwb.add_acquisition(
    miniscope_loader.external_image_series(
        name="behaviorCam",
        file_pattern="behavCam*avi",
    )
)

save_path = os.path.join(data_dir, "test_out.nwb")
with NWBHDF5IO(save_path, "w") as io:
    io.write(nwb)

# test read
with NWBHDF5IO(save_path, "r") as io:
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
under construction
