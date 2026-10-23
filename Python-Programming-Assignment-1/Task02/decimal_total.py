"""Demonstrate Python values and exact Decimal payment totals."""

from decimal import Decimal
import sys


def total_float(items: list[str]) -> float:
    """Return the sum after converting the original strings to binary floats."""
    total = 0.0
    for amount in items:
        total += float(amount)
    return total


def total_decimal(items: list[str]) -> Decimal:
    """Sum decimal text exactly, without an intermediate binary float."""
    total = Decimal("0.00")
    for amount in items:
        total += Decimal(amount)
    return total


def main() -> None:
    payments = ["33.40"] * 1000 + ["0.10"] * 3
    print("type(10):", type(10))
    print("type(10.0):", type(10.0))
    print('type("10"):', type("10"))
    print("type(True):", type(True))
    print("type([10, 8.5]):", type([10, 8.5]))
    print("7 / 2:", 7 / 2)
    print("7 // 2:", 7 // 2)
    print("7 % 2:", 7 % 2)
    print("-7 // 2:", -7 // 2)
    print("0.1 + 0.2 == 0.3:", 0.1 + 0.2 == 0.3)
    print("float total:", total_float(payments))
    print("Decimal total:", total_decimal(payments))
    print(
        "float equality / Decimal equality:",
        0.1 + 0.2 == 0.3,
        Decimal("0.1") + Decimal("0.2") == Decimal("0.3"),
    )
    print(
        "object sizes (bytes):",
        sys.getsizeof(3340),
        sys.getsizeof(33.40),
        sys.getsizeof(Decimal("33.40")),
    )
    print("integer-paise total:", 1000 * 3340 + 3 * 10)


if __name__ == "__main__":
    main()
