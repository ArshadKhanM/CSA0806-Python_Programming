"""Benchmark float and Decimal summation for the assignment record counts."""

from decimal import Decimal
from time import perf_counter


SIZES = (300, 6000, 150000)


def benchmark(count: int) -> tuple[float, Decimal, Decimal, float, float]:
    """Return both totals, their displayed difference, and elapsed seconds."""
    amounts = ["33.40"] * count + ["0.10"] * 3

    start = perf_counter()
    float_total = sum(float(value) for value in amounts)
    float_seconds = perf_counter() - start

    start = perf_counter()
    decimal_total = sum(
        (Decimal(value) for value in amounts), Decimal("0.00")
    )
    decimal_seconds = perf_counter() - start

    difference = Decimal(str(float_total)) - decimal_total
    return float_total, decimal_total, difference, float_seconds, decimal_seconds


def main() -> None:
    print("N | float total | Decimal total | Decimal(str(float))-Decimal | float s | Decimal s")
    for count in SIZES:
        float_total, exact_total, difference, float_seconds, decimal_seconds = benchmark(count)
        expected = Decimal(count) * Decimal("33.40") + Decimal("0.30")
        if exact_total != expected:
            raise ArithmeticError(
                f"Decimal benchmark mismatch for N={count}: "
                f"expected {expected}, got {exact_total}"
            )
        print(
            f"{count} | {float_total!r} | {exact_total:.2f} | {difference} | "
            f"{float_seconds:.6f} | {decimal_seconds:.6f}"
        )


if __name__ == "__main__":
    main()
