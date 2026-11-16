import csv
import tempfile
import unittest
from pathlib import Path

from Task02.monthly_attendance import process_month


class MonthlyAttendanceTests(unittest.TestCase):
    def test_processes_each_file_once_and_writes_all_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "input"
            output = root / "output"
            source.mkdir()
            (source / "attendance_2026-10-01.csv").write_text(
                "1,2026-10-01,P\n2,2026-10-01,A\nbroken\n", encoding="utf-8"
            )
            (source / "attendance_2026-10-02.csv").write_text(
                "1,2026-10-02,P\n2,2026-10-02,A\n", encoding="utf-8"
            )
            result = process_month(source, "2026-10", output)
            self.assertEqual(result["counts"], {"1": [2, 0], "2": [0, 2]})
            self.assertEqual(len(result["errors"]), 1)
            with (output / "below_75.csv").open(encoding="utf-8", newline="") as file:
                self.assertEqual(list(csv.reader(file))[1], ["2", "0.00"])
            self.assertTrue((output / "damaged_records.csv").exists())

    def test_empty_month_produces_headers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = process_month(temporary, "2026-10", Path(temporary) / "out")
            self.assertEqual(result["counts"], {})
            self.assertEqual(result["errors"], [])

    def test_missing_folder_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = process_month(
                Path(temporary) / "missing", "2026-10", Path(temporary) / "out"
            )
            self.assertEqual(len(result["errors"]), 1)
            self.assertEqual(result["errors"][0].reason, "input folder does not exist")


if __name__ == "__main__":
    unittest.main()
