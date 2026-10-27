import tempfile
import unittest
from pathlib import Path

from tests.helpers import TempDirCase  # noqa: F401  (puts py_modules on the path)
from steamling_control import gamepad


def tweaks(kind, enabled=True):
    return {"global": {}, "games": {"5": {"enabled": enabled, "gamepadType": kind}}}


class GamepadTest(unittest.TestCase):
    def setUp(self):
        gamepad._applied["kind"] = None
        self.calls = []
        self._tmp = tempfile.TemporaryDirectory()
        self.state = Path(self._tmp.name) / "gamepad-target"
        self.addCleanup(self._tmp.cleanup)
        real = gamepad.sync_gamepad
        self.sync = lambda appid, **kw: real(appid, state=self.state, **kw)

    def switch(self, kind):
        self.calls.append(kind)
        self.state.write_text(kind + "\n")
        return True

    def test_merge_follows_the_enabled_switch(self):
        self.assertEqual(gamepad.gamepad_for(tweaks("ds5"), "5"), "ds5")
        self.assertEqual(gamepad.gamepad_for(tweaks("ds5", enabled=False), "5"), "")
        self.assertEqual(gamepad.gamepad_for(tweaks("joycon"), "5"), "")
        self.assertEqual(gamepad.gamepad_for(tweaks("ds5"), None), "")

    def test_untouched_session_is_left_alone(self):
        self.sync("9", switch=self.switch, tweaks=tweaks("ds5"))
        self.sync(None, switch=self.switch, tweaks=tweaks("ds5"))
        self.assertEqual(self.calls, [])

    def test_switch_for_the_game_and_back_after(self):
        self.sync("5", switch=self.switch, tweaks=tweaks("xb360"))
        self.sync("5", switch=self.switch, tweaks=tweaks("xb360"))  # no repeat
        self.sync(None, switch=self.switch, tweaks=tweaks("xb360"))
        self.sync(None, switch=self.switch, tweaks=tweaks("xb360"))  # already back
        self.assertEqual(self.calls, ["xb360", "deck-uhid"])

    def test_desktop_took_over(self):
        self.sync("5", switch=self.switch, tweaks=tweaks("ds5"))
        self.state.write_text("xb360\n")  # steamling-desktop on the way into desktop mode
        self.sync(None, switch=self.switch, tweaks=tweaks("ds5"))
        self.assertEqual(self.calls, ["ds5"])
        self.assertIsNone(gamepad._applied["kind"])

    def test_failed_switch_is_retried(self):
        self.sync("5", switch=lambda kind: False, tweaks=tweaks("ds5"))
        self.sync("5", switch=self.switch, tweaks=tweaks("ds5"))
        self.assertEqual(self.calls, ["ds5"])


if __name__ == "__main__":
    unittest.main()
