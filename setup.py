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
    "version": "0.5.0",
    "description": "Represent metadata for Miniscope acquisition system.",
    "long_description": long_description,
    "long_description_content_type": "text/markdown",
    "author": "Ben Dichter",
    "author_email": "ben.dichter@catalystneuro.com",
    "url": "https://github.com/catalystneuro/ndx-miniscope",
    "license": "BSD-3",
    "install_requires": install_requires,
    "packages": find_packages("src/pynwb", exclude=["tests", "tests.*"]),
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
    "keywords": [
        "NeurodataWithoutBorders",
        "NWB",
        "nwb-extension",
        "ndx-extension",
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
