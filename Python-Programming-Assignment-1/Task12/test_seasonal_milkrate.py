"""Automated tests for seasonal rates and ten-day volume bonus rules."""

import unittest
from decimal import Decimal as D

from Task12.seasonal_milkrate import seasonal_rate, steps, ten_day_payment


class SeasonalMilkRateTests(unittest.TestCase):
    def test_seasonal_rate_examples(self) -> None:
        self.assertEqual(seasonal_rate(D("3.56"), D("8.50"), "STANDARD"), D("30.40"))
        self.assertEqual(seasonal_rate(D("3.56"), D("8.50"), "APR_JUN"), D("32.45"))

    def test_step_tie_rounds_half_up(self) -> None:
        self.assertEqual(steps(D("3.55"), D("3.50"), D("0.10")), D("1"))

    def test_bonus_requires_more_than_500_litres(self) -> None:
        self.assertEqual(
            ten_day_payment(D("520"), D("3.50"), D("8.50"), "APR_JUN", D("520")),
            D("16900.00"),
        )
        self.assertEqual(
            ten_day_payment(D("500"), D("3.50"), D("8.50"), "APR_JUN", D("500")),
            D("16000.00"),
        )
        self.assertEqual(
            ten_day_payment(D("501"), D("3.50"), D("8.50"), "APR_JUN", D("501")),
            D("16282.50"),
        )

    def test_invalid_season_and_volume_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Season must"):
            seasonal_rate(D("3.5"), D("8.5"), "UNKNOWN")
        with self.assertRaisesRegex(ValueError, "cannot be less"):
            ten_day_payment(D("2"), D("3.5"), D("8.5"), "STANDARD", D("1"))

    def test_quality_bounds_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Fat must"):
            seasonal_rate(D("7.01"), D("8.5"), "STANDARD")
        with self.assertRaisesRegex(ValueError, "SNF must"):
            seasonal_rate(D("3.5"), D("10.01"), "STANDARD")
        with self.assertRaisesRegex(ValueError, "Fat must"):
            seasonal_rate(3.5, D("8.5"), "STANDARD")


if __name__ == "__main__":
    unittest.main()
