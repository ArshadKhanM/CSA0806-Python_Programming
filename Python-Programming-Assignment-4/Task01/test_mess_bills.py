import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from Task01.mess_bills import process_mess_file


class MessBillTests(unittest.TestCase):
    def test_exact_decimal_total_and_rejected_line_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "mess.csv"
            path.write_text(
                "1,A,1250.50\n2,B,980.00\nbroken,row\n3,C,125.75\n\n",
                encoding="utf-8",
            )
            result = process_mess_file(path)
        self.assertEqual(result.total, Decimal("2356.25"))
        self.assertEqual(len(result.report_lines), 3)
        self.assertEqual(result.rejected[0].line_number, 3)
        self.assertEqual(result.rejected[0].reason, "expected 3 fields, found 2")

    def test_bad_amount_and_empty_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "mess.csv"
            path.write_text("1,A,not-money\n", encoding="utf-8")
            result = process_mess_file(path)
            self.assertEqual(result.total, Decimal("0.00"))
            self.assertEqual(result.rejected[0].line_number, 1)
            path.write_text("", encoding="utf-8")
            self.assertEqual(process_mess_file(path).report_lines, [])


if __name__ == "__main__":
    unittest.main()
