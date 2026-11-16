import csv
import tempfile
import unittest
from pathlib import Path

from Task06.fest.pipeline import process_department_folder
from Task06.fest.validation import InvalidRegistration, parse_registration, valid_email


class FestPipelineTests(unittest.TestCase):
    def test_email_validation_and_line_parsing(self) -> None:
        self.assertTrue(valid_email("student.name@example.edu"))
        self.assertFalse(valid_email("invalid-address"))
        self.assertEqual(
            parse_registration(
                "192311001,Asha,CS,asha@example.edu,Drama;Music"
            ).events,
            {"Drama", "Music"},
        )
        with self.assertRaises(InvalidRegistration):
            parse_registration("192311001,Asha,CS,bad-email,Drama")

    def test_pipeline_handles_duplicate_invalid_damaged_and_missing_files(self) -> None:
        package_root = Path(__file__).parent
        sample = package_root / "sample_input"
        with tempfile.TemporaryDirectory() as temporary:
            result = process_department_folder(sample, temporary)
            self.assertEqual(len(result["master"]), 4)
            self.assertEqual(result["duplicates"], 1)
            self.assertEqual(len(result["errors"]), 3)
            master = result["master"]["192311001"]
            self.assertEqual(master.events, {"Drama", "Music", "Quiz"})
            with (Path(temporary) / "master.csv").open(encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 4)
            self.assertTrue((Path(temporary) / "event_drama.csv").exists())
            error_text = (Path(temporary) / "errors.log").read_text(encoding="utf-8")
            self.assertIn("invalid email", error_text)
            self.assertIn("expected 5 fields", error_text)
            self.assertIn("department_05.csv:0", error_text)
            self.assertTrue((Path(temporary) / "summary.txt").exists())

    def test_empty_input_still_writes_headers_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = process_department_folder(Path(temporary) / "missing", temporary)
            self.assertEqual(result["master"], {})
            self.assertEqual(len(result["errors"]), 5)
            with (Path(temporary) / "master.csv").open(encoding="utf-8", newline="") as file:
                self.assertEqual(next(csv.reader(file)), ["register", "name", "department", "email", "events"])


if __name__ == "__main__":
    unittest.main()
