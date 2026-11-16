"""Rainfall totals, rolling averages, and timing experiments."""

import argparse
import math
import random
import time
from collections.abc import Sequence


def weekly_totals(readings: Sequence[float], days_per_week: int = 7) -> list[float]:
    """Return seven-day totals, including a final partial week when present."""
    if days_per_week <= 0:
        raise ValueError("days_per_week must be positive")
    return [
        sum(readings[start : start + days_per_week])
        for start in range(0, len(readings), days_per_week)
    ]


def extrema(readings: Sequence[float]) -> tuple[tuple[int, float], tuple[int, float]] | None:
    """Return (wettest day, driest day) as 1-based (day, reading) pairs."""
    if not readings:
        return None
    wettest = max(enumerate(readings, start=1), key=lambda item: item[1])
    driest = min(enumerate(readings, start=1), key=lambda item: item[1])
    return wettest, driest


def moving_average_naive(readings: Sequence[float], window: int = 7) -> list[float]:
    if window <= 0:
        raise ValueError("window must be positive")
    return [
        sum(readings[start : start + window]) / window
        for start in range(len(readings) - window + 1)
    ]


def moving_average_running(readings: Sequence[float], window: int = 7) -> list[float]:
    """Calculate a fixed-width moving average by updating a running sum."""
    if window <= 0:
        raise ValueError("window must be positive")
    if len(readings) < window:
        return []
    current = sum(readings[:window])
    averages = [current / window]
    for index in range(window, len(readings)):
        current += readings[index] - readings[index - window]
        averages.append(current / window)
    return averages


def dry_days(readings: Sequence[float]) -> list[int]:
    """Return 1-based day numbers with zero rainfall."""
    return [day for day, amount in enumerate(readings, start=1) if amount == 0]


def addition_counts(n: int, window: int = 7) -> tuple[int, int]:
    """Return (naive additions, running-sum additions), excluding subtractions."""
    if window <= 0:
        raise ValueError("window must be positive")
    if n < window:
        return 0, 0
    windows = n - window + 1
    return windows * (window - 1), (window - 1) + (n - window)


def benchmark(sizes: Sequence[int] = (365, 36_500, 365_000)) -> None:
    rng = random.Random(2026)
    for size in sizes:
        readings = [rng.random() * 100 for _ in range(size)]
        results = []
        for method in (moving_average_naive, moving_average_running):
            start = time.perf_counter()
            values = method(readings)
            elapsed = time.perf_counter() - start
            results.append((values, elapsed))
        if len(results[0][0]) != len(results[1][0]) or any(
            not math.isclose(first, second, rel_tol=1e-12, abs_tol=1e-12)
            for first, second in zip(results[0][0], results[1][0])
        ):
            raise AssertionError("moving-average implementations disagree")
        print(
            f"{size:>7} readings: naive={results[0][1]:.6f}s, "
            f"running={results[1][1]:.6f}s, additions={addition_counts(size)}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()
    if args.benchmark:
        benchmark()
        return
    readings = [0, 3, 5, 0, 12, 4, 8, 2, 0, 7, 1, 0, 6, 9]
    print("weekly totals:", weekly_totals(readings))
    print("wettest/driest day:", extrema(readings))
    print("7-day averages:", moving_average_running(readings))
    print("dry days:", dry_days(readings))
    print("slices [7:14], [-7:], [::7]:", readings[7:14], readings[-7:], readings[::7])
    print("addition counts for 365 readings:", addition_counts(365))


if __name__ == "__main__":
    main()
