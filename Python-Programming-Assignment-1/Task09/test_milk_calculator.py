"""Automated tests for Task 9 validation and collection calculations."""

import unittest
from decimal import Decimal as D

from Task05.input_validation import parse_decimal, validate_entry
from Task09.milk_calculator import calculate_entry, demo


class InputValidationTests(unittest.TestCase):
    def test_decimal_parser_accepts_whitespace(self) -> None:
        self.assertEqual(parse_decimal(" 8.5 ", "litres"), D("8.5"))

    def test_decimal_parser_rejects_invalid_and_non_finite_values(self) -> None:
        for text in ("eight", "8,5", "", "NaN", "Infinity"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_decimal(text, "litres")

    def test_validation_checks_id_shift_and_snf_range(self) -> None:
        with self.assertRaisesRegex(ValueError, "Farmer ID"):
            validate_entry(" ", D("1"), D("3.5"), D("8.5"), "MORNING")
        with self.assertRaisesRegex(ValueError, "Shift"):
            validate_entry("F1", D("1"), D("3.5"), D("8.5"), "NIGHT")
        with self.assertRaisesRegex(ValueError, "SNF must be"):
            validate_entry("F1", D("1"), D("3.5"), D("10.1"), "MORNING")

    def test_minimum_and_maximum_fat_are_inclusive(self) -> None:
        self.assertEqual(
            calculate_entry("F1", D("1"), D("2"), D("8.5"), "morning").payment,
            D("24.00"),
        )
        self.assertEqual(
            calculate_entry("F2", D("1"), D("7"), D("8.5"), "evening").payment,
            D("44.00"),
        )

    def test_reference_examples_and_hand_total(self) -> None:
        entries = demo()
        self.assertEqual([item.payment for item in entries], [
            D("300.00"), D("283.90"), D("333.60"), D("24.00"), D("44.00")
        ])
        self.assertEqual(sum((item.payment for item in entries), D("0.00")), D("985.50"))

    def test_negative_litres_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            calculate_entry("F1", D("-1"), D("3.5"), D("8.5"), "MORNING")


if __name__ == "__main__":
    unittest.main()
