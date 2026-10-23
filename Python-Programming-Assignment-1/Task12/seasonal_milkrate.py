"""Season-aware milk rate calculator with ten-day volume bonus."""

from decimal import Decimal, ROUND_HALF_UP

from Task03.constants import (
    CENT,
    FAT_REFERENCE,
    FAT_STEP,
    MAX_FAT,
    MAX_SNF,
    MIN_FAT,
    MIN_SNF,
    ONE,
    SNF_REFERENCE,
    SNF_STEP,
    SNF_STEP_VALUE,
)
from Task05.input_validation import validate_entry

D = Decimal
STANDARD = {
    "base": D("30.00"),
    "fat_value": D("0.40"),
}
APR_JUN = {
    "base": D("32.00"),
    "fat_value": D("0.45"),
}
RATE_CARDS = {
    "STANDARD": STANDARD,
    "APR_JUN": APR_JUN,
}
BONUS_THRESHOLD = D("500")
BONUS_PER_LITRE = D("0.50")


def steps(reading: Decimal, reference: Decimal, step: Decimal) -> Decimal:
    """Return nearest whole measurement steps with half-up tie handling."""
    return ((reading - reference) / step).quantize(
        ONE, rounding=ROUND_HALF_UP
    )


def seasonal_rate(fat: Decimal, snf: Decimal, season: str) -> Decimal:
    """Calculate a rounded per-litre rate for a known season."""
    if not isinstance(season, str) or season.strip().upper() not in RATE_CARDS:
        raise ValueError("Season must be STANDARD or APR_JUN.")
    if not isinstance(fat, Decimal) or not fat.is_finite() or not MIN_FAT <= fat <= MAX_FAT:
        raise ValueError("Fat must be between 2.00 and 7.00 inclusive.")
    if not isinstance(snf, Decimal) or not snf.is_finite() or not MIN_SNF <= snf <= MAX_SNF:
        raise ValueError("SNF must be between 6.00 and 10.00 inclusive.")

    card = RATE_CARDS[season.strip().upper()]
    rate = (
        card["base"]
        + steps(fat, FAT_REFERENCE, FAT_STEP) * card["fat_value"]
        + steps(snf, SNF_REFERENCE, SNF_STEP) * SNF_STEP_VALUE
    )
    return rate.quantize(CENT, rounding=ROUND_HALF_UP)


def ten_day_payment(
    litres: Decimal,
    fat: Decimal,
    snf: Decimal,
    season: str,
    ten_day_litres: Decimal,
    farmer_id: str = "FARMER",
    shift: str = "MORNING",
) -> Decimal:
    """Calculate an entry payment using the farmer's aggregate volume."""
    validate_entry(farmer_id, litres, fat, snf, shift)
    if not isinstance(ten_day_litres, Decimal) or not ten_day_litres.is_finite():
        raise ValueError("Ten-day litres must be a finite Decimal value.")
    if ten_day_litres < litres:
        raise ValueError("Ten-day litres cannot be less than this collection.")
    rate = seasonal_rate(fat, snf, season)
    bonus = BONUS_PER_LITRE if ten_day_litres > BONUS_THRESHOLD else D("0.00")
    return (litres * (rate + bonus)).quantize(CENT, rounding=ROUND_HALF_UP)


def main() -> None:
    """Print the required seasonal and threshold examples."""
    print(seasonal_rate(D("3.56"), D("8.50"), "STANDARD"))
    print(seasonal_rate(D("3.56"), D("8.50"), "APR_JUN"))
    print(ten_day_payment(D("520"), D("3.50"), D("8.50"), "APR_JUN", D("520")))
    print(ten_day_payment(D("500"), D("3.50"), D("8.50"), "APR_JUN", D("500")))
    print(ten_day_payment(D("501"), D("3.50"), D("8.50"), "APR_JUN", D("501")))


if __name__ == "__main__":
    main()
