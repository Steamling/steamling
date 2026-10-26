import unittest

from tests.helpers import TempDirCase  # noqa: F401  (puts py_modules on the path)
from steamling_control import calibration


class StickParamsTest(unittest.TestCase):
    def test_symmetric_stick(self):
        p = calibration.stick_params("axis_leftx", 1000, 10, -1000, -10)
        self.assertEqual(p["axis_leftx_center"], 0)
        self.assertEqual(p["axis_leftx_max"], 950)
        self.assertEqual(p["axis_leftx_min"], -950)
        # 150% of the mean rest noise, but never below 5% of the range
        self.assertEqual(p["axis_leftx_deadzone"], 47)

    def test_off_centre_stick_is_recentred(self):
        p = calibration.stick_params("axis_lefty", 1100, 110, -900, 90)
        self.assertEqual(p["axis_lefty_center"], -100)
        self.assertEqual(p["axis_lefty_max"], 950)

    def test_noisy_stick_gets_a_bigger_deadzone(self):
        p = calibration.stick_params("axis_rightx", 1000, 100, -1000, -100)
        self.assertEqual(p["axis_rightx_deadzone"], 150)
        self.assertEqual(p["axis_rightx_antideadzone"], 120)


class TriggerParamsTest(unittest.TestCase):
    def test_coupled_trigger_moves_its_reference_to_rest(self):
        p = calibration.trigger_params("trigger_left", 1500, 100, coupled=True)
        self.assertEqual(p["trigger_left_max"], 1400)
        self.assertEqual(p["trigger_left_deadzone"], 5)

    def test_fixed_reference_trigger_covers_its_rest_reading(self):
        p = calibration.trigger_params("trigger_right", 1500, 100, coupled=False)
        self.assertEqual(p["trigger_right_max"], 1500)
        self.assertEqual(p["trigger_right_deadzone"], 105)


class ParseTest(unittest.TestCase):
    def test_parse_kv_skips_comments_and_junk(self):
        text = "# header\naxis_leftx_max=900\nbroken\naxis_lefty_max = 880 \nx=notanumber\n"
        self.assertEqual(calibration._parse_kv(text), {"axis_leftx_max": 900, "axis_lefty_max": 880})


if __name__ == "__main__":
    unittest.main()
