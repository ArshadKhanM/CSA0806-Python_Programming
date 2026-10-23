"""Tests for the reusable Task 7 milk-rate module."""

import unittest
from decimal import Decimal as D

from Task05.input_validation import validate_entry
from Task07.milkrate import payout, rate_per_litre, ten_day_total


class MilkRateTests(unittest.TestCase):
    def test_reference_above_and_below_rates(self) -> None:
        self.assertEqual(rate_per_litre(D("3.5"), D("8.5")), D("30.00"))
        self.assertEqual(payout(D("8.5"), D("4.2"), D("8.7")), D("283.90"))
        self.assertEqual(payout(D("12"), D("3.1"), D("8.3")), D("333.60"))

    def test_fat_boundaries(self) -> None:
        self.assertEqual(payout(D("1"), D("2.0"), D("8.5")), D("24.00"))
        self.assertEqual(payout(D("1"), D("7.0"), D("8.5")), D("44.00"))

    def test_rounding_is_half_up(self) -> None:
        self.assertEqual(payout(D("0.0005"), D("3.5"), D("8.5")), D("0.02"))

    def test_total_sums_rounded_payments(self) -> None:
        self.assertEqual(
            ten_day_total([D("300.00"), D("283.90"), D("333.60"), D("24"), D("44")]),
            D("985.50"),
        )

    def test_invalid_entry_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            validate_entry("F001", D("-1"), D("3.5"), D("8.5"), "MORNING")
        with self.assertRaisesRegex(ValueError, "Fat must be"):
            validate_entry("F002", D("1"), D("7.1"), D("8.5"), "EVENING")


if __name__ == "__main__":
    unittest.main()
