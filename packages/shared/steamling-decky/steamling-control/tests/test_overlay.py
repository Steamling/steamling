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
            overlay.set_overlay("fps", self.tmp / "missing.conf")

    def test_set_rewrites_the_same_file(self):
        path = self.write("steamling-mangohud.conf", "no_display\n")
        inode = path.stat().st_ino
        self.assertEqual(overlay.set_overlay("full", path), {"available": True, "level": "full"})
        self.assertEqual(path.read_text(), "preset=4\n")
        # mangoapp watches the inode, so the file must be written in place, never replaced
        self.assertEqual(path.stat().st_ino, inode)

    def test_unknown_level(self):
        path = self.write("steamling-mangohud.conf", "no_display\n")
        with self.assertRaises(ValueError):
            overlay.set_overlay("loud", path)
