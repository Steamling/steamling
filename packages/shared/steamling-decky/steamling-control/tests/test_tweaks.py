import json
import unittest
from unittest import mock

from tests.helpers import TempDirCase
from steamling_control import tweaks
from steamling_control.touch import touch_disabled_for

CONTRACT = {
    "defaults": {"global": {"disableXalia": True}, "games": {}},
    "profiles": {
        "default": {"label": "Default", "config": {"TSOEnabled": "1"}},
        "fast": {"label": "Fast", "config": {"TSOEnabled": "0"}, "steam": "TSOEnabled:0"},
    },
}


class TweaksTest(TempDirCase):
    def setUp(self):
        super().setUp()
        self.contract = self.write("fex-profiles.json", json.dumps(CONTRACT))
        self.tweaks = self.tmp / "game-tweaks.json"
        patches = [mock.patch.object(tweaks, "FEX_PROFILES_CONFIG", self.contract),
                   mock.patch.object(tweaks, "TWEAKS_CONFIG", self.tweaks)]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_missing_file_gives_the_contract_defaults(self):
        self.assertEqual(tweaks.load_tweaks(), CONTRACT["defaults"])

    def test_saved_values_merge_over_defaults_and_bad_games_are_dropped(self):
        self.tweaks.write_text(json.dumps({
            "global": {"fexProfile": "fast"},
            "games": {"123": {"enabled": 1}, "not-an-id": {"enabled": True}, "456": "junk"},
        }))
        loaded = tweaks.load_tweaks()
        self.assertEqual(loaded["global"], {"disableXalia": True, "fexProfile": "fast"})
        self.assertEqual(loaded["games"], {"123": {"enabled": True}})

    def test_corrupt_file_falls_back_to_defaults(self):
        self.tweaks.write_text("{not json")
        self.assertEqual(tweaks.load_tweaks(), CONTRACT["defaults"])

    def test_sanitize_rejects_non_objects_and_huge_payloads(self):
        with self.assertRaises(ValueError):
            tweaks.sanitize_tweaks([])
        with self.assertRaises(ValueError):
            tweaks.sanitize_tweaks({"global": {"x": "y" * 300000}})

    def test_save_round_trips(self):
        tweaks.save_tweaks({"global": {"audioLatency": "90"}, "games": {"7": {"enabled": True}, "x": {}}})
        saved = json.loads(self.tweaks.read_text())
        self.assertEqual(saved, {"global": {"audioLatency": "90"}, "games": {"7": {"enabled": True}}})

    def test_profile_labels_carry_the_steam_string(self):
        labels = tweaks.fex_profile_labels(tweaks.load_fex_contract())
        self.assertEqual(labels["fast"]["steam"], "TSOEnabled:0")
        self.assertEqual(labels["default"]["steam"], "")


class TouchMergeTest(unittest.TestCase):
    def test_per_game_value_only_counts_while_enabled(self):
        data = {"global": {"touchDisabled": False}, "games": {"1": {"enabled": False, "touchDisabled": True}}}
        self.assertFalse(touch_disabled_for(data, "1"))
        data["games"]["1"]["enabled"] = True
        self.assertTrue(touch_disabled_for(data, "1"))

    def test_no_game_means_touch_on(self):
        self.assertFalse(touch_disabled_for({"global": {"touchDisabled": True}}, None))


if __name__ == "__main__":
    unittest.main()
