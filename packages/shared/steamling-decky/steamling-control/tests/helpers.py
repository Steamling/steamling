import sys
import tempfile
import unittest
from pathlib import Path

# The plugin's backend modules live in py_modules/, which Decky puts on the path at runtime.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "py_modules"))


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        path = self.tmp / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path
