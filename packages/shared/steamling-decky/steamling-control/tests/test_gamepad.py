import unittest

from tests.helpers import TempDirCase  # noqa: F401  (puts py_modules on the path)
from steamling_control import gamepad


def tweaks(kind, enabled=True):
    return {"global": {}, "games": {"5": {"enabled": enabled, "gamepadType": kind}}}


class GamepadTest(unittest.TestCase):
    def setUp(self):
        gamepad._applied["kind"] = None
        self.calls = []

    def switch(self, kind):
        self.calls.append(kind)
        return True

    def test_merge_follows_the_enabled_switch(self):
        self.assertEqual(gamepad.gamepad_for(tweaks("ds5"), "5"), "ds5")
        self.assertEqual(gamepad.gamepad_for(tweaks("ds5", enabled=False), "5"), "")
        self.assertEqual(gamepad.gamepad_for(tweaks("joycon"), "5"), "")
        self.assertEqual(gamepad.gamepad_for(tweaks("ds5"), None), "")

    def test_untouched_session_is_left_alone(self):
        gamepad.sync_gamepad("9", switch=self.switch, tweaks=tweaks("ds5"))
        gamepad.sync_gamepad(None, switch=self.switch, tweaks=tweaks("ds5"))
        self.assertEqual(self.calls, [])

    def test_switch_for_the_game_and_back_after(self):
        gamepad.sync_gamepad("5", switch=self.switch, tweaks=tweaks("xb360"))
        gamepad.sync_gamepad("5", switch=self.switch, tweaks=tweaks("xb360"))  # no repeat
        gamepad.sync_gamepad(None, switch=self.switch, tweaks=tweaks("xb360"))
        gamepad.sync_gamepad(None, switch=self.switch, tweaks=tweaks("xb360"))  # already back
        self.assertEqual(self.calls, ["xb360", "deck-uhid"])

    def test_failed_switch_is_retried(self):
        gamepad.sync_gamepad("5", switch=lambda kind: False, tweaks=tweaks("ds5"))
        gamepad.sync_gamepad("5", switch=self.switch, tweaks=tweaks("ds5"))
        self.assertEqual(self.calls, ["ds5"])


if __name__ == "__main__":
    unittest.main()
