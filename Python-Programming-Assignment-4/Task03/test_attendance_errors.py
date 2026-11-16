import tempfile
import unittest
from pathlib import Path

from Task03.attendance_errors import (
    AttendanceFileError,
    InvalidRecord,
    parse_line,
    summarise,
)


class AttendanceErrorTests(unittest.TestCase):
    def test_complete_code_expected_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "attendance.csv"
            path.write_text(
                "192311001,2026-10-08,P\n"
                "192311002,2026-10-08,A\n"
                "192311003,2026-10-08\n"
                "192311004,2026-10-08,L\n",
                encoding="utf-8",
            )
            self.assertEqual(
                summarise(path),
                (1, 1, [(3, "expected 3 fields, found 2"), (4, "invalid status 'L'")]),
            )

    def test_parse_rejects_bad_fields(self) -> None:
        with self.assertRaisesRegex(InvalidRecord, "expected 3 fields"):
            parse_line("1,2026-10-08")

    def test_missing_file_is_wrapped_with_original_cause(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(AttendanceFileError) as caught:
                summarise(Path(temporary) / "missing.csv")
        self.assertIsInstance(caught.exception.__cause__, FileNotFoundError)

    def test_empty_file_returns_zero_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "empty.csv"
            path.write_text("", encoding="utf-8")
            self.assertEqual(summarise(path), (0, 0, []))


if __name__ == "__main__":
    unittest.main()
