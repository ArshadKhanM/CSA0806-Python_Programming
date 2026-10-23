"""Rate card module and demonstration for the original payment rules."""

from decimal import Decimal

from Task06.payment_functions import payout, rate_per_litre, ten_day_total


def main() -> None:
    """Print the reference examples without side effects on import."""
    examples = (
        (Decimal("10"), Decimal("3.5"), Decimal("8.5")),
        (Decimal("8.5"), Decimal("4.2"), Decimal("8.7")),
        (Decimal("12"), Decimal("3.1"), Decimal("8.3")),
    )
    for litres, fat, snf in examples:
        rate = rate_per_litre(fat, snf)
        payment = payout(litres, fat, snf)
        print(
            f"{litres:5} L fat {fat} SNF {snf} "
            f"rate {rate:6.2f} payment {payment:8.2f}"
        )
    print("total:", ten_day_total([payout(*entry) for entry in examples]))


if __name__ == "__main__":
    main()
