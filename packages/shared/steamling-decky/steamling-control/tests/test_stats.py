from tests.helpers import TempDirCase
from steamling_control import stats


class StatsTest(TempDirCase):
    def test_cpu_load_needs_two_samples(self):
        stats._last_cpu.update(total=None, idle=None)
        self.assertIsNone(stats.cpu_load("cpu  100 0 100 800 0 0 0 0\n"))
        # 100 more ticks, 25 of them idle
        self.assertEqual(stats.cpu_load("cpu  150 0 125 825 0 0 0 0\n"), 75)

    def test_clusters_in_mhz(self):
        for n, cur, top in ((0, 1785600, 2016000), (3, 2803200, 2803200)):
            self.write(f"cpufreq/policy{n}/scaling_cur_freq", f"{cur}\n")
            self.write(f"cpufreq/policy{n}/cpuinfo_max_freq", f"{top}\n")
            self.write(f"cpufreq/policy{n}/related_cpus", f"{n}\n")
        out = stats.cpu_clusters(self.tmp / "cpufreq")
        self.assertEqual([c["mhz"] for c in out], [1785, 2803])
        self.assertEqual(out[0]["maxMhz"], 2016)

    def test_gpu_from_devfreq(self):
        self.write("devfreq/1d84000.ufshc/cur_freq", "300000000\n")
        self.write("devfreq/3d00000.gpu/cur_freq", "680000000\n")
        self.write("devfreq/3d00000.gpu/max_freq", "680000000\n")
        self.assertEqual(stats.gpu(self.tmp / "devfreq"), {"mhz": 680, "maxMhz": 680})

    def test_hottest_zone_per_kind(self):
        for n, kind, temp in ((0, "cpu0-thermal", 41000), (1, "cpuss-1", 55000), (2, "gpuss-0", 48000), (3, "battery", 99000)):
            self.write(f"thermal/thermal_zone{n}/type", kind)
            self.write(f"thermal/thermal_zone{n}/temp", str(temp))
        self.assertEqual(stats.temperatures(self.tmp / "thermal"), {"cpu": 55, "gpu": 48})

    def test_battery_prefers_current_times_voltage(self):
        self.write("ps/battery/type", "Battery")
        self.write("ps/battery/capacity", "84")
        self.write("ps/battery/status", "Discharging")
        self.write("ps/battery/current_now", "-1500000")
        self.write("ps/battery/voltage_now", "4000000")
        self.write("ps/battery/power_now", "1")
        self.write("ps/battery/temp", "312")
        self.write("ps/usb/type", "USB")
        out = stats.battery(self.tmp / "ps")
        self.assertEqual(out, {"percent": 84, "status": "Discharging", "watts": 6.0, "tempC": 31})

    def test_memory(self):
        text = "MemTotal:       11811160 kB\nMemFree:  100 kB\nMemAvailable:    7616424 kB\n"
        self.assertEqual(stats.memory(text), {"usedMb": 4096, "totalMb": 11534})
