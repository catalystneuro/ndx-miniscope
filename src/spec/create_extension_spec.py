from export_spec import export_spec
from pynwb.spec import NWBGroupSpec, NWBNamespaceBuilder


def main():
    ns_builder = NWBNamespaceBuilder(
        doc="holds metadata relevant for miniscope acquisition",
        name="ndx-miniscope",
        version="0.4.0",
        author="Ben Dichter",
        contact="ben.dichter@catalystneuro.com",
    )

    Miniscope = NWBGroupSpec(
        neurodata_type_def="Miniscope",
        neurodata_type_inc="Device",
        doc="The extension of Device to hold metadata specific to Miniscopes.",
    )
    Miniscope.add_attribute(
        name="compression",
        doc="The type of compression CODEC. GREY is no compression. FFV1 losslessly compresses.",
        dtype="text",
        required=False,
    )
    Miniscope.add_attribute(
        name="deviceType",
        doc="A device type supported by Miniscope-DAQ Software (e.g., 'Miniscope_V4_BNO', 'Miniscope_V3').",
        dtype="text",
        required=False,
    )
    Miniscope.add_attribute(
        name="frameRate",
        doc="Frame rate (e.g., 20FPS)",
        dtype="text",
        required=False,
    )
    Miniscope.add_attribute(
        name="framesPerFile",
        doc="The number of frames stored per file.",
        dtype="int",
        required=False,
    )
    Miniscope.add_attribute(
        name="gain",
        doc="Gain settings corresponding to Low, Medium, High.",
        dtype="text",
        required=False,
    )
    Miniscope.add_attribute(
        name="led0",
        doc="Excitation LED intensity (range 0 - 100).",
        dtype="int",
        required=False,
    )
    Miniscope.add_attribute(name="excitation", doc="The magnitude of excitation.", dtype="int", required=False)
    Miniscope.add_attribute(name="msCamExposure", doc="The exposure of camera (max=255).", dtype="int", required=False)

    Miniscope.add_dataset(
        name="ROI",
        doc="The bounding box (height x width) of the portion of the video that is saved to disk.",
        shape=(None,),
        dtype="int",
        quantity="?",
    )

    ns_builder.include_type("Device", namespace="core")

    export_spec(ns_builder, [Miniscope])


if __name__ == "__main__":
    main()
