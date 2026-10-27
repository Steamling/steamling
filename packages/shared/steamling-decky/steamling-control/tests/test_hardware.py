from tests.helpers import TempDirCase
from steamling_control import hardware


class HardwareTest(TempDirCase):
    def test_fan_needs_a_pwm(self):
        self.write("hwmon/hwmon0/temp1_input", "40000")
        self.assertFalse(hardware.has_fan(self.tmp / "hwmon"))
        self.write("hwmon/hwmon2/pwm1", "0")
        self.assertTrue(hardware.has_fan(self.tmp / "hwmon"))

    def test_scheduler_needs_binary_kernel_and_helper(self):
        binary, helper = self.tmp / "scx_lavd", self.tmp / "steamling-lavd-mode"
        sched_ext = self.tmp / "sched_ext"
        self.assertFalse(hardware.has_scheduler(binary, sched_ext, helper))
        binary.write_text("")
        helper.write_text("")
        self.assertFalse(hardware.has_scheduler(binary, sched_ext, helper))
        sched_ext.mkdir()
        self.assertTrue(hardware.has_scheduler(binary, sched_ext, helper))

    def test_pad_switch_needs_inputplumber_and_the_helper(self):
        daemon, tool = self.tmp / "inputplumber", self.tmp / "steamling-gamepad-target"
        tool.write_text("")
        self.assertFalse(hardware.has_pad_switch(daemon, tool))
        daemon.write_text("")
        self.assertTrue(hardware.has_pad_switch(daemon, tool))
