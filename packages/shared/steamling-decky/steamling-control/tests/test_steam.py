from tests.helpers import TempDirCase
from steamling_control import steam


class LibraryTest(TempDirCase):
    def test_library_folders_and_manifests(self):
        lib = self.write("steamapps/libraryfolders.vdf",
                         f'"libraryfolders"\n{{\n "1"\n {{\n  "path"  "{self.tmp}/sd"\n }}\n}}\n')
        self.write("steamapps/appmanifest_10.acf", '"AppState"\n{\n "appid" "10"\n "name" "Zeta"\n}\n')
        self.write("sd/steamapps/appmanifest_20.acf", '"AppState"\n{\n "appid" "20"\n "name" "alpha"\n}\n')
        # the same game in two libraries is listed once
        self.write("sd/steamapps/appmanifest_10.acf", '"AppState"\n{\n "appid" "10"\n "name" "Zeta"\n}\n')
        dirs = steam._steamapps_dirs([lib])
        self.assertIn(self.tmp / "sd/steamapps", dirs)
        dirs.append(self.tmp / "steamapps")
        games = steam._scan(sorted(set(dirs)))
        self.assertEqual([g["name"] for g in games], ["alpha", "Zeta"])
