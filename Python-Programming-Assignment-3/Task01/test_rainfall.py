import unittest
import math

from Task01.rainfall import (
    addition_counts,
    dry_days,
    extrema,
    moving_average_naive,
    moving_average_running,
    weekly_totals,
)


class RainfallTests(unittest.TestCase):
    def test_weekly_totals_include_partial_final_week(self) -> None:
        self.assertEqual(weekly_totals(list(range(1, 10))), [28, 17])

    def test_extrema_and_dry_days_are_one_based(self) -> None:
        values = [0, 4, 0, 8]
        self.assertEqual(extrema(values), ((4, 8), (1, 0)))
        self.assertEqual(dry_days(values), [1, 3])
        self.assertIsNone(extrema([]))

    def test_moving_averages_and_short_inputs(self) -> None:
        values = list(range(1, 10))
        self.assertEqual(moving_average_naive(values), moving_average_running(values))
        self.assertEqual(moving_average_running(values), [4.0, 5.0, 6.0])
        self.assertEqual(moving_average_running([]), [])
        self.assertEqual(moving_average_naive([1, 2]), [])

    def test_addition_counts(self) -> None:
        self.assertEqual(addition_counts(10), (24, 9))
        self.assertEqual(addition_counts(6), (0, 0))
        with self.assertRaises(ValueError):
            moving_average_running([1], window=0)

    def test_running_sum_matches_naive_with_float_rounding(self) -> None:
        values = [0.1] * 100
        naive = moving_average_naive(values)
        running = moving_average_running(values)
        self.assertTrue(
            all(math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12)
                for left, right in zip(naive, running))
        )


if __name__ == "__main__":
    unittest.main()
