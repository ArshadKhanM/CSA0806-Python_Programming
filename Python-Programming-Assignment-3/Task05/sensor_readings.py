"""Clean temperature readings with loops, comprehensions, and iterators."""

import argparse
import random
import sys
import time
from collections.abc import Iterable


def analyze_loop(readings: Iterable[float]) -> tuple[list[float], list[float], list[int]]:
    valid_c: list[float] = []
    fahrenheit: list[float] = []
    alarms: list[int] = []
    for minute, value in enumerate(readings):
        if -50 <= value <= 50:
            valid_c.append(value)
            fahrenheit.append(value * 9 / 5 + 32)
            if value < 2 or value > 8:
                alarms.append(minute)
    return valid_c, fahrenheit, alarms


def analyze_comprehension(
    readings: Iterable[float],
) -> tuple[list[float], list[float], list[int]]:
    values = list(readings)
    valid = [value for value in values if -50 <= value <= 50]
    fahrenheit = [value * 9 / 5 + 32 for value in valid]
    alarms = [
        minute
        for minute, value in enumerate(values)
        if -50 <= value <= 50 and (value < 2 or value > 8)
    ]
    return valid, fahrenheit, alarms


def analyze_map_filter(
    readings: Iterable[float],
) -> tuple[list[float], list[float], list[int]]:
    values = list(readings)
    valid = list(filter(lambda value: -50 <= value <= 50, values))
    fahrenheit = list(map(lambda value: value * 9 / 5 + 32, valid))
    alarms = list(
        map(
            lambda pair: pair[0],
            filter(
                lambda pair: -50 <= pair[1] <= 50 and (pair[1] < 2 or pair[1] > 8),
                enumerate(values),
            ),
        )
    )
    return valid, fahrenheit, alarms


def benchmark(sizes: tuple[int, ...] = (10_000, 100_000, 1_000_000)) -> None:
    rng = random.Random(5)
    for size in sizes:
        readings = [rng.uniform(-60, 60) for _ in range(size)]
        expected = None
        for name, method in (
            ("loop", analyze_loop),
            ("comprehension", analyze_comprehension),
            ("map/filter", analyze_map_filter),
        ):
            start = time.perf_counter()
            result = method(readings)
            elapsed = time.perf_counter() - start
            if expected is None:
                expected = result
            elif expected != result:
                raise AssertionError("sensor-cleaning implementations disagree")
            print(f"{size:>9} {name:14}: {elapsed:.6f}s")
            del result
    materialized = [value for value in readings if -50 <= value <= 50]
    generator = (value for value in readings if -50 <= value <= 50)
    print("container bytes (list, generator):", sys.getsizeof(materialized), sys.getsizeof(generator))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()
    readings = [4.0, 10.0, 52.0, -55.0, 1.0]
    print("loop:", analyze_loop(readings))
    print("comprehension:", analyze_comprehension(readings))
    print("map/filter:", analyze_map_filter(readings))
    print("dictionary comprehension:", {i: value for i, value in enumerate(readings) if -50 <= value <= 50})
    print("set comprehension:", {value for value in readings if -50 <= value <= 50})
    print("enumerated alarms:", analyze_comprehension(readings)[2])
    if args.benchmark:
        benchmark()


if __name__ == "__main__":
    main()
