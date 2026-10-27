from tests.helpers import TempDirCase
from steamling_control import overlay


class OverlayTest(TempDirCase):
    def test_levels_read_back(self):
        self.assertEqual(overlay.level_of("no_display\n"), "off")
        self.assertEqual(overlay.level_of(""), "off")
        self.assertEqual(overlay.level_of("preset=3\n"), "detailed")
        self.assertEqual(overlay.level_of("# steam\npreset=2,3\nfps_limit=30\n"), "compact")
        self.assertEqual(overlay.level_of("fps\ngpu_stats\n"), "custom")

    def test_not_in_game_mode(self):
        status = overlay.overlay_status(self.tmp / "missing.conf")
        self.assertEqual(status, {"available": False, "level": "off"})
        with self.assertRaises(RuntimeError):
            overlay.set_overlay("fps", self.tmp / "missing.conf", self.tmp / "overlay.json")

    def test_set_rewrites_the_same_file(self):
        path = self.write("steamling-mangohud.conf", "no_display\n")
        inode = path.stat().st_ino
        self.assertEqual(overlay.set_overlay("full", path, self.tmp / "overlay.json"),
                         {"available": True, "level": "full"})
        self.assertEqual(path.read_text(), "preset=4\n")
        # mangoapp watches the inode, so the file must be written in place, never replaced
        self.assertEqual(path.stat().st_ino, inode)

    def test_unknown_level(self):
        path = self.write("steamling-mangohud.conf", "no_display\n")
        with self.assertRaises(ValueError):
            overlay.set_overlay("loud", path, self.tmp / "overlay.json")

    def test_pick_is_saved(self):
        path = self.write("steamling-mangohud.conf", "no_display\n")
        saved = self.tmp / "overlay.json"
        overlay.set_overlay("compact", path, saved)
        self.assertEqual(overlay.saved_level(saved), "compact")

    def test_reassert_puts_the_pick_back_after_steam(self):
        path = self.write("steamling-mangohud.conf", "no_display\n")
        saved = self.tmp / "overlay.json"
        overlay.set_overlay("detailed", path, saved)
        path.write_text("no_display\n")
        inode = path.stat().st_ino
        overlay.reassert_overlay(path, saved, delays=(0,), sleep=lambda s: None)
        self.assertEqual(path.read_text(), "preset=3\n")
        self.assertEqual(path.stat().st_ino, inode)

    def test_reassert_without_a_pick_leaves_steam_alone(self):
        path = self.write("steamling-mangohud.conf", "preset=1\n")
        overlay.reassert_overlay(path, self.tmp / "none.json", delays=(0,), sleep=lambda s: None)
        self.assertEqual(path.read_text(), "preset=1\n")
