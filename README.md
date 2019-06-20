# ndx-miniscope Extension for NWB:N

This is a Neurodata Extension (NDX) for Neurodata Without Borders: Neurophysiology (NWB:N) 2.0 for Miniscope acquisition data.

The Miniscope acquisition software generally outputs the following files:

* msCam[##].avi
* behavCam[##].avi
* timestamp.dat
* settings_and_notes.dat

This repo provides an extension to the `Device` core NWB neurodata_type called `Miniscope` which contains fields for the data in `settings_and_notes.dat`. The following code demonstrates how to use this extension to properly convert Miniscope acquisition data into NWB by creating external links, which does not require the video data to be copied into the NWB file.

## python
### Installation
```bash
pip install ndx-miniscope
```

### Usage


```python
import os
import pandas as pd
from ndx_miniscope import Miniscope
from pynwb import NWBFile, NWBHDF5IO
from datetime import datetime
from dateutil.tz import tzlocal
from pynwb.image import ImageSeries
from natsort import natsorted
from glob import glob


def load_miniscope_timestamps(fpath, cam_num=1):
    if not fpath[-4:] == '.dat':
        fpath = os.path.join(fpath, 'timestamp.dat')
    df = pd.read_csv(fpath, sep='\t')
    df_cam = df[df['camNum'] == cam_num]
    tt = df_cam['sysClock'].values/1000
    tt[0] = 0

    return tt


data_dir = 'path/to/data_dir'

settings_and_notes_file = os.path.join(data_dir, 'settings_and_notes.dat')

df = pd.read_csv(settings_and_notes_file, sep='\t').loc[0]

session_start_time = datetime(2017, 4, 15, 12, tzinfo=tzlocal())

nwb = NWBFile('session_description', 'identifier', session_start_time)

miniscope = Miniscope(name='Miniscope', excitation=int(df['excitation']),
                      msCamExposure=int(df['msCamExposure']),
                      recordLength=int(df['recordLength']))

nwb.add_device(miniscope)

ms_files = [os.path.split(x)[1] for x in
            natsorted(glob(os.path.join(data_dir, 'msCam*.avi')))]

behav_files = [os.path.split(x)[1] for x in
               natsorted(glob(os.path.join(data_dir, 'behavCam*.avi')))]

nwb.add_acquisition(
    ImageSeries(
        name='OnePhotonSeries',
        format='external',
        external_file=ms_files,
        timestamps=load_miniscope_timestamps(data_dir),
        starting_frame=[0] * len(ms_files)
    )
)

nwb.add_acquisition(
    ImageSeries(
        name='behaviorCam',
        format='external',
        external_file=behav_files,
        timestamps=load_miniscope_timestamps(data_dir, cam_num=2),
        starting_frame=[0] * len(behav_files)
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
under construction
