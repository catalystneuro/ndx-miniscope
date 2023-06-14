import os

from pynwb import get_class, load_namespaces

name = "ndx-miniscope"

here = os.path.abspath(os.path.dirname(__file__))
ndx_miniscope_spec_path = os.path.join(here, "spec", name + ".namespace.yaml")

load_namespaces(ndx_miniscope_spec_path)

Miniscope = get_class("Miniscope", name)
