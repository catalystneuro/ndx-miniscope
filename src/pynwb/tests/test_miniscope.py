from copy import deepcopy
from datetime import datetime
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from warnings import warn

from hdmf.testing import TestCase
from numpy.testing import assert_array_equal

from ndx_miniscope import Miniscope
from pynwb import NWBHDF5IO, NWBFile


class TestMiniscope(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session_start_time = datetime.now().astimezone()

        cls.miniscope_behav_cam_metadata = dict(
            name="BehavCam_2",
            compression="MJPG",
            deviceType="WebCam-1920x1080",
            frameRate="15FPS",
            framesPerFile=1000,
            ROI=[720, 1280],  # "ROI": {"height": 720, "leftEdge": 0, "topEdge": 0, "width": 1280},
        )

        cls.miniscope_mscam_metadata = dict(
            name="Miniscope",
            compression="FFV1",
            deviceType="Miniscope_V3",
            frameRate="15FPS",
            framesPerFile=1000,
            gain="High",
            led0=47,
        )

        cls.test_dir = Path(mkdtemp())

    @classmethod
    def tearDownClass(cls):
        try:
            rmtree(cls.test_dir)
        except PermissionError:  # Windows CI bug
            warn(f"Unable to fully clean the temporary directory: {cls.test_dir}\n\nPlease remove it manually.")

    def setUp(self):
        self.nwbfile = NWBFile(
            session_description="session_description",
            identifier="file_id",
            session_start_time=self.session_start_time,
        )

    def test_miniscope_defaults(self):
        device = Miniscope(name=self.miniscope_mscam_metadata["name"])
        self.nwbfile.add_device(device)
        self.assertIn(device.name, self.nwbfile.devices)

    def test_miniscope_roundtrip(self):
        device = Miniscope(**self.miniscope_mscam_metadata)
        self.nwbfile.add_device(device)

        nwbfile_path = self.test_dir / "test_miniscope_nwb.nwb"
        with NWBHDF5IO(nwbfile_path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(nwbfile_path, mode="r") as io:
            nwbfile_in = io.read()
            device_metadata = deepcopy(self.miniscope_mscam_metadata)
            device_name = device_metadata.pop("name")
            self.assertIn(device_name, nwbfile_in.devices)
            device_in = nwbfile_in.devices[device_name]
            self.assertDictEqual(device_in.fields, device_metadata)

    def test_miniscope_behavcam_roundtrip(self):
        device = Miniscope(**self.miniscope_behav_cam_metadata)
        self.nwbfile.add_device(device)

        nwbfile_path = self.test_dir / "test_miniscope_behavcam.nwb"

        with NWBHDF5IO(nwbfile_path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(nwbfile_path, mode="r") as io:
            nwbfile_in = io.read()
            device_metadata = deepcopy(self.miniscope_behav_cam_metadata)
            device_name = device_metadata.pop("name")
            self.assertIn(device_name, nwbfile_in.devices)

            device_in = nwbfile_in.devices[device_name]

            ROI = device_metadata.pop("ROI")
            ROI_in = device_in.fields.pop("ROI")[:]

            self.assertDictEqual(device_in.fields, device_metadata)
            assert_array_equal(ROI, ROI_in)
