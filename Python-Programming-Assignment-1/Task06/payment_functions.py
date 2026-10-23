"""Reusable rate, payment, and ten-day total functions."""

from decimal import Decimal

from Task04.expressions import calculate_payment, calculate_rate


def rate_per_litre(fat: Decimal, snf: Decimal) -> Decimal:
    """Return the rounded rate for the original rate card."""
    return calculate_rate(fat, snf)


def payout(litres: Decimal, fat: Decimal, snf: Decimal) -> Decimal:
    """Return one farmer's payment rounded to the nearest paisa."""
    return calculate_payment(litres, rate_per_litre(fat, snf))


def ten_day_total(payments: list[Decimal]) -> Decimal:
    """Sum payments that have already been rounded individually."""
    return sum(payments, Decimal("0.00")).quantize(Decimal("0.01"))


def main() -> None:
    from decimal import Decimal as D

    payment = payout(D("8.5"), D("4.2"), D("8.7"))
    print("rate:", rate_per_litre(D("4.2"), D("8.7")))
    print("payment:", payment)
    print("two-payment total:", ten_day_total([payment, D("300.00")]))


if __name__ == "__main__":
    main()
