import json

from tests.helpers import TempDirCase
from steamling_control import suggestions


class SuggestionsTest(TempDirCase):
    def test_shipped_file_parses(self):
        self.assertIsInstance(suggestions.load_suggestions(local=self.tmp / "none.json"), dict)

    def test_local_overrides_and_filters(self):
        shipped = self.write("shipped.json", json.dumps({"games": {
            "10": {"name": "A", "settings": {"fexProfile": "fast"}, "note": "shipped"},
            "20": {"name": "B", "settings": {"fexProfile": "compatible"}},
        }}))
        local = self.write("local.json", json.dumps({"games": {
            "20": {"name": "B", "settings": {"audioLatency": "90", "rm -rf": "x", "fanMode": 3}, "note": "mine"},
            "abc": {"settings": {"fexProfile": "fast"}},
            "30": {"name": "empty"},
        }}))
        out = suggestions.load_suggestions(shipped, local)
        self.assertEqual(sorted(out), ["10", "20"])
        self.assertEqual(out["20"]["settings"], {"audioLatency": "90"})
        self.assertEqual(out["20"]["note"], "mine")
        self.assertEqual(out["10"]["proton"], "")

    def test_broken_files_are_ignored(self):
        bad = self.write("bad.json", "{")
        self.assertEqual(suggestions.load_suggestions(bad, bad), {})
