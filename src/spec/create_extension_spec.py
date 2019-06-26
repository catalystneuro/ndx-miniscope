
from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec

from export_spec import export_spec


def main():
    ns_builder = NWBNamespaceBuilder(doc='holds metadata relevant for miniscope acquisition',
                                     name='ndx-miniscope',
                                     version='0.2.1',
                                     author='Ben Dichter',
                                     contact='ben.dichter@gmail.com')

    Miniscope = NWBGroupSpec(neurodata_type_def='Miniscope', neurodata_type_inc='Device',
                             doc='extension of Device to hold metadata specific to Miniscopes')
    Miniscope.add_attribute(name='excitation', doc='magnitude of excitation', dtype='int', required=False)
    Miniscope.add_attribute(name='msCamExposure', doc='exposure of camera (max=255)', dtype='int', required=False)

    ns_builder.include_type('Device', namespace='core')

    export_spec(ns_builder, [Miniscope])


if __name__ == "__main__":
    main()
