import os

import pandas as pd
from pynwb import load_namespaces, get_class

name = 'ndx-miniscope'

here = os.path.abspath(os.path.dirname(__file__))
ns_path = os.path.join(here, 'spec', name + '.namespace.yaml')

load_namespaces(ns_path)

Miniscope = get_class('Miniscope', name)


def load_miniscope_timestamps(fpath, cam_num=1):
    if not fpath[-4:] == '.dat':
        fpath = os.path.join(fpath, 'timestamp.dat')
    df = pd.read_csv(fpath, sep='\t')
    df_cam = df[df['camNum'] == cam_num]
    tt = df_cam['sysClock'].values/1000
    tt[0] = 0
    return tt


def read_settings_and_notes(fpath):
    if not fpath[-4:] == '.dat':
        fpath = os.path.join(fpath, 'settings_and_notes.dat')
    df = pd.read_csv(fpath, sep='\t').loc[0]

    return {n: int(df[n]) for n in
            ['excitation', 'msCamExposure', 'recordLength'] if n in df}
