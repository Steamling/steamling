import unittest
from unittest import mock

from tests.helpers import TempDirCase
from steamling_control import tuning

BASE = {
    "axis_leftx_deadzone": 100, "axis_leftx_antideadzone": 80, "axis_leftx_max": 1000, "axis_leftx_min": -1000,
    "axis_lefty_deadzone": 100, "axis_lefty_antideadzone": 80, "axis_lefty_max": 1000, "axis_lefty_min": -1000,
    "axis_rightx_deadzone": 60, "axis_rightx_antideadzone": 48, "axis_rightx_max": 900, "axis_rightx_min": -900,
    "axis_righty_center": 5,
}


class TunedTest(unittest.TestCase):
    def test_neutral_tuning_changes_nothing(self):
        out = tuning.tuned(BASE, {"left": dict(tuning.DEFAULT), "right": dict(tuning.DEFAULT)})
        self.assertEqual(out, {k: v for k, v in BASE.items() if not k.endswith("center")})

    def test_each_stick_scales_on_its_own(self):
        out = tuning.tuned(BASE, {"left": {"deadzone": 200, "outer": 90}, "right": {"deadzone": 50, "outer": 100}})
        self.assertEqual(out["axis_leftx_deadzone"], 200)
        self.assertEqual(out["axis_leftx_antideadzone"], 160)
        self.assertEqual(out["axis_lefty_max"], 900)
        self.assertEqual(out["axis_lefty_min"], -900)
        self.assertEqual(out["axis_rightx_deadzone"], 30)
        self.assertEqual(out["axis_rightx_max"], 900)
        self.assertNotIn("axis_righty_center", out)


class FileTest(TempDirCase):
    def test_load_rejects_odd_values(self):
        path = self.write("tuning.conf", "left_deadzone=150\nleft_outer=42\nright_deadzone=9999\n")
        self.assertEqual(tuning.load(path), {"left": {"deadzone": 150, "outer": 100},
                                             "right": {"deadzone": 100, "outer": 100}})

    def test_set_writes_and_applies(self):
        path = self.tmp / "tuning.conf"
        with mock.patch.object(tuning, "TUNING", path), \
             mock.patch.object(tuning, "apply") as apply, \
             mock.patch.object(tuning.calibration, "_driver", return_value=(None, None, None)):
            tuning.set_tuning("right", 150, 95)
            with self.assertRaises(ValueError):
                tuning.set_tuning("middle", 100, 100)
        self.assertIn("right_deadzone=150", path.read_text())
        self.assertEqual(apply.call_args[0][0]["right"], {"deadzone": 150, "outer": 95})


if __name__ == "__main__":
    unittest.main()
