from tests.helpers import TempDirCase
from steamling_control import cache


class CacheTest(TempDirCase):
    def setUp(self):
        super().setUp()
        self.libs = [self.tmp / "a/steamapps", self.tmp / "b/steamapps"]
        self.write("a/steamapps/shadercache/42/fozpipelinesv6/steam_pipeline_cache.foz", "x" * 1000)
        self.write("b/steamapps/shadercache/42/DXVK_state_cache/game.dxvk-cache", "y" * 500)
        self.write("a/steamapps/shadercache/7/keep.bin", "z" * 10)

    def test_size_spans_every_library(self):
        self.assertEqual(cache.cache_info("42", self.libs), {"appid": "42", "bytes": 1500})
        self.assertEqual(cache.cache_info("99", self.libs)["bytes"], 0)

    def test_clear_only_touches_that_game(self):
        self.assertEqual(cache.clear_cache("42", None, self.libs)["bytes"], 0)
        self.assertFalse((self.tmp / "a/steamapps/shadercache/42").exists())
        self.assertTrue((self.tmp / "a/steamapps/shadercache/7/keep.bin").exists())

    def test_running_game_is_refused(self):
        with self.assertRaises(RuntimeError):
            cache.clear_cache("42", "42", self.libs)
        self.assertEqual(cache.cache_info("42", self.libs)["bytes"], 1500)

    def test_bad_appid(self):
        with self.assertRaises(ValueError):
            cache.cache_info("../etc", self.libs)
