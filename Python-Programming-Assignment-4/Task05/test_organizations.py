import tempfile
import unittest
from pathlib import Path

from Task05.attendance_package.main import run as package_run
from Task05.attendance_package.attendance.stats import absent_three_days
from Task05.module_import.main import run as module_run
from Task05.single_script.attendance_single import run as single_run
from Task05.three_modules.main import run as three_module_run


class OrganizationTests(unittest.TestCase):
    def test_all_four_organizations_return_same_reports(self) -> None:
        sample = Path(__file__).with_name("sample_attendance.csv")
        runners = (single_run, module_run, three_module_run, package_run)
        results = []
        for run in runners:
            with tempfile.TemporaryDirectory() as output:
                results.append(run(sample, output))
        for result in results[1:]:
            self.assertEqual(result, results[0])
        self.assertEqual(results[0]["streaks"], ["192311001"])
        self.assertAlmostEqual(results[0]["percentages"]["192311002"], 2 / 3 * 100)

    def test_streak_requires_three_consecutive_calendar_days(self) -> None:
        rows = [
            ("1", "2026-10-01", "A"),
            ("1", "2026-10-02", "A"),
            ("2", "2026-10-01", "A"),
            ("2", "2026-10-03", "A"),
        ]
        self.assertEqual(absent_three_days(rows), [])


if __name__ == "__main__":
    unittest.main()
