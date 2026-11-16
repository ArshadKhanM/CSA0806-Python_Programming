import tempfile
import unittest
from pathlib import Path

from Task04.returns_log import flawed_process, process_returns


class ReturnLogTests(unittest.TestCase):
    def test_flawed_version_keeps_only_last_day_and_joins_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "returns.log"
            days = []
            for number, content in enumerate(("A\nB\n", "C\n", "D\nE\n"), start=1):
                day = root / f"day{number}.txt"
                day.write_text(content, encoding="utf-8")
                days.append(day)
                flawed_process(day, log)
            self.assertEqual(log.read_text(encoding="utf-8"), "DE")

    def test_safe_version_appends_lines_and_logs_missing_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            day, log, errors = root / "day.txt", root / "returns.log", root / "errors.log"
            day.write_text("A-1\nA-2\n", encoding="utf-8")
            self.assertTrue(process_returns(day, log, errors))
            self.assertTrue(process_returns(day, log, errors))
            self.assertFalse(process_returns(root / "missing", log, errors))
            self.assertEqual(log.read_text(encoding="utf-8"), "A-1\nA-2\nA-1\nA-2\n")
            self.assertIn("FileNotFoundError", errors.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
