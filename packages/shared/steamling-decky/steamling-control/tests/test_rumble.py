import json
import struct
from unittest import mock

from tests.helpers import TempDirCase
from steamling_control import rumble


class RumbleTest(TempDirCase):
    def setUp(self):
        super().setUp()
        self.switch = self.write("module/rsinput/parameters/rumble_enable", "1")
        self.write("input/event3/device/name", "qcom-hv-haptics\n")
        self.write("input/event1/device/name", "rsinput-gamepad\n")
        self.motor = self.write("dev/event3", "")
        p = mock.patch.object(rumble, "CONFIG", self.tmp / "rumble.json")
        p.start()
        self.addCleanup(p.stop)

    def apply(self, settings):
        rumble.apply(settings, self.tmp / "module", self.tmp / "input", self.tmp / "dev")

    def test_defaults_without_a_saved_choice(self):
        status = rumble.rumble_status(self.tmp / "module", self.tmp / "input")
        self.assertEqual(status, {"canSwitch": True, "canScale": True, "enabled": True, "strength": 100})

    def test_off_and_half_strength(self):
        self.apply({"enabled": False, "strength": 50})
        self.assertEqual(self.switch.read_text(), "0")
        _sec, _usec, ev_type, code, value = struct.unpack("llHHi", self.motor.read_bytes())
        self.assertEqual((ev_type, code), (rumble.EV_FF, rumble.FF_GAIN))
        self.assertEqual(value, round(0x7FFF / 2))

    def test_gain_scales_per_driver(self):
        self.assertEqual(rumble.gain_for(100, 0x7FFF), 0x7FFF)
        self.assertEqual(rumble.gain_for(25, 0xFFFF), 16384)

    def test_bad_saved_values_fall_back(self):
        (self.tmp / "rumble.json").write_text(json.dumps({"enabled": "yes", "strength": 33}))
        self.assertEqual(rumble.load(), rumble.DEFAULTS)
        with self.assertRaises(ValueError):
            rumble.set_rumble(True, 33)
