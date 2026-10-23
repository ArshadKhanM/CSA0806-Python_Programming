"""Decimal expressions for quality steps, rates, and rounded payments."""

from decimal import Decimal, ROUND_HALF_UP

from Task03.constants import (
    BASE_RATE,
    CENT,
    FAT_REFERENCE,
    FAT_STEP,
    FAT_STEP_VALUE,
    ONE,
    SNF_REFERENCE,
    SNF_STEP,
    SNF_STEP_VALUE,
)


def nearest_steps(value: Decimal, reference: Decimal, step: Decimal) -> Decimal:
    """Return the signed nearest whole number of measurement steps."""
    return ((value - reference) / step).quantize(ONE, rounding=ROUND_HALF_UP)


def calculate_rate(fat: Decimal, snf: Decimal) -> Decimal:
    """Calculate the original rate and round it to the nearest paisa."""
    fat_steps = nearest_steps(fat, FAT_REFERENCE, FAT_STEP)
    snf_steps = nearest_steps(snf, SNF_REFERENCE, SNF_STEP)
    unrounded_rate = (
        BASE_RATE + fat_steps * FAT_STEP_VALUE + snf_steps * SNF_STEP_VALUE
    )
    return unrounded_rate.quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_payment(litres: Decimal, rate: Decimal) -> Decimal:
    """Calculate one payment, rounded to the nearest paisa."""
    return (litres * rate).quantize(CENT, rounding=ROUND_HALF_UP)


def main() -> None:
    fat = Decimal("4.2")
    snf = Decimal("8.7")
    print("fat steps:", nearest_steps(fat, FAT_REFERENCE, FAT_STEP))
    print("SNF steps:", nearest_steps(snf, SNF_REFERENCE, SNF_STEP))
    print("rate:", calculate_rate(fat, snf))
    print("payment:", calculate_payment(Decimal("8.5"), calculate_rate(fat, snf)))
    print("float 0.1 + 0.2:", 0.1 + 0.2)
    print("Decimal half-up example:", Decimal("2.5").quantize(ONE, rounding=ROUND_HALF_UP))
    print("built-in round tie-to-even:", round(2.5))


if __name__ == "__main__":
    main()
