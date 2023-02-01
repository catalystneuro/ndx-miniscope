# -*- coding: utf-8 -*-

import os
from pathlib import Path
from shutil import copy2

from setuptools import find_packages, setup

path = Path(__file__).parent

with open(os.path.join(path, "README.md")) as f:
    long_description = f.read()

with open(path / "requirements.txt") as f:
    install_requires = f.readlines()

setup_args = {
    "name": "ndx-miniscope",
    "version": "0.3.0",
    "description": "holds metadata relevant for miniscope acquisition",
    "long_description": long_description,
    "author": "Ben Dichter",
    "author_email": "ben.dichter@catalystneuro.com",
    "url": "https://github.com/catalystneuro/ndx-miniscope",
    "license": "",
    "install_requires": install_requires,
    "packages": find_packages("src/pynwb"),
    "package_dir": {"": "src/pynwb"},
    "package_data": {
        "ndx_miniscope": [
            "spec/ndx-miniscope.namespace.yaml",
            "spec/ndx-miniscope.extensions.yaml",
        ]
    },
    "classifiers": [
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    "zip_safe": False,
}


def _copy_spec_files(project_dir):
    ns_path = os.path.join(project_dir, "spec", "ndx-miniscope.namespace.yaml")
    ext_path = os.path.join(project_dir, "spec", "ndx-miniscope.extensions.yaml")

    dst_dir = os.path.join(project_dir, "src", "pynwb", "ndx_miniscope", "spec")
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)

    copy2(ns_path, dst_dir)
    copy2(ext_path, dst_dir)


if __name__ == "__main__":
    _copy_spec_files(os.path.dirname(__file__))
    setup(**setup_args)
