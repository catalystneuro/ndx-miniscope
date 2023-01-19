from pynwb.spec import NWBNamespaceBuilder, NWBGroupSpec

from export_spec import export_spec

# See also https://github.com/Aharoni-Lab/Miniscope-DAQ-QT-Software/blob/master/deviceConfigs/userConfigProps.json


def main():
    ns_builder = NWBNamespaceBuilder(
        doc="holds metadata relevant for miniscope acquisition",
        name="ndx-miniscope",
        version="0.2.3",
        author="Ben Dichter, Chris Brozdowski",
        contact="ben.dichter@gmail.com, cbroz@datajoint.com",
    )

    Miniscope = NWBGroupSpec(
        neurodata_type_def="Miniscope",
        neurodata_type_inc="Device",
        doc="extension of Device to hold metadata specific to Miniscopes",
    )
    Miniscope.add_attribute(
        name="version",
        doc="Miniscope version e.g., V3, V4",
        dtype="text",
        required=True,
    )
    Miniscope.add_attribute(
        name="excitation", doc="magnitude of excitation", dtype="int", required=False
    )
    Miniscope.add_attribute(
        name="msCamExposure",
        doc="exposure of camera (max=255)",
        dtype="int",
        required=False,
    )
    Miniscope.add_attribute(
        name="ROI",
        doc="The bounding box of the portion of the video that is saved to disk. Edges are zero-indexed",
        dtype="int",
        dims=["height, leftEdge, topEdge, width"],
        shape=[4],
        required=False,
    )
    Miniscope.add_attribute(
        name="compression",
        doc="Compression CODEC. GREY is no compression. FFV1 losslessly compresses.",
        dtype="text",
        required=False,
    )
    Miniscope.add_attribute(
        name="deviceType",
        doc="A device type supported by Miniscope-DAQ Software (e.g., Miniscope_V4_BNO)",
        dtype="text",
        required=False,
    )
    Miniscope.add_attribute(
        name="ewl",
        doc="position of the electro-tunable lens focal plane. ElectroWetting Lens value range (-127 - 127)",
        dtype="int",
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
        doc="Frames stored per file",
        dtype="int",
        required=False,
    )
    Miniscope.add_attribute(
        name="gain",
        doc="Gain settings (1, 2, 3.5) corresponding to Low, Medium, High",
        dtype="float32",
        required=False,
    )
    Miniscope.add_attribute(
        name="led0",
        doc="Excitation LED intensity (range 0 - 100)",
        dtype="int",
        required=False,
    )

    ns_builder.include_type("Device", namespace="core")

    export_spec(ns_builder, [Miniscope])


if __name__ == "__main__":
    main()
