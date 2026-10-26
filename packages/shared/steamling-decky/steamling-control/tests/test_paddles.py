import json
import unittest

from tests.helpers import TempDirCase
from steamling_control import paddles


def targets(profile, source):
    return [m["target_events"] for m in profile["mapping"] if m["source_event"] == {"gamepad": {"button": source}}]


class ProfileTest(unittest.TestCase):
    def test_no_remap_is_the_stock_profile(self):
        profile = paddles.build_profile("", "")
        self.assertEqual(profile["mapping"], paddles.STOCK_MAPPINGS)

    def test_left_paddle_to_a(self):
        profile = paddles.build_profile("South", "")
        self.assertEqual(targets(profile, "LeftPaddle1"), [[{"gamepad": {"button": "South"}}]])
        # the LeftTop alias follows the remap instead of the stock LeftTop -> LeftPaddle1
        self.assertEqual(targets(profile, "LeftTop"), [[{"gamepad": {"button": "South"}}]])
        self.assertEqual(targets(profile, "RightTop"), [[{"gamepad": {"button": "RightPaddle1"}}]])
        self.assertEqual(targets(profile, "RightPaddle1"), [])

    def test_profile_is_plain_json_inputplumber_can_read(self):
        text = json.dumps(paddles.build_profile("LeftStick", "RightStick"))
        self.assertIn('"kind": "DeviceProfile"', text)


class LoadTest(TempDirCase):
    def test_round_trip(self):
        path = self.write("p.json", json.dumps(paddles.build_profile("East", "Start")))
        self.assertEqual(paddles.load(path), {"left": "East", "right": "Start"})

    def test_missing_or_junk(self):
        self.assertEqual(paddles.load(self.tmp / "none.json"), {"left": "", "right": ""})
        path = self.write("bad.json", "[1,2]")
        self.assertEqual(paddles.load(path), {"left": "", "right": ""})

    def test_unknown_target_rejected(self):
        with self.assertRaises(ValueError):
            paddles.set_paddles("Turbo", "")


if __name__ == "__main__":
    unittest.main()
