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
