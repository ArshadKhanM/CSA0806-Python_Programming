"""Input parsing and validation for milk collection records."""

from decimal import Decimal, InvalidOperation

from Task03.constants import (
    ALLOWED_SHIFTS,
    MAX_FAT,
    MAX_SNF,
    MIN_FAT,
    MIN_SNF,
)


def parse_decimal(text: str, field_name: str = "value") -> Decimal:
    """Parse finite decimal text, raising a readable ValueError on failure."""
    if not isinstance(text, str):
        raise ValueError(f"{field_name} must be entered as decimal text.")
    cleaned = text.strip()
    try:
        value = Decimal(cleaned)
    except InvalidOperation as error:
        raise ValueError(
            f"Invalid {field_name}: enter a decimal such as 8.5."
        ) from error
    if not value.is_finite():
        raise ValueError(f"{field_name} must be a finite decimal number.")
    return value


def validate_entry(
    farmer_id: str,
    litres: Decimal,
    fat: Decimal,
    snf: Decimal,
    shift: str,
) -> None:
    """Raise ValueError if an entry does not meet the collection rules."""
    if not isinstance(farmer_id, str) or not farmer_id.strip():
        raise ValueError("Farmer ID is required.")
    for label, value in (("Litres", litres), ("Fat", fat), ("SNF", snf)):
        if not isinstance(value, Decimal) or not value.is_finite():
            raise ValueError(f"{label} must be a finite Decimal value.")
    if litres <= 0:
        raise ValueError("Litres must be greater than zero.")
    if not MIN_FAT <= fat <= MAX_FAT:
        raise ValueError("Fat must be between 2.00 and 7.00 inclusive.")
    if not MIN_SNF <= snf <= MAX_SNF:
        raise ValueError("SNF must be between 6.00 and 10.00 inclusive.")
    if not isinstance(shift, str) or shift.strip().upper() not in ALLOWED_SHIFTS:
        raise ValueError("Shift must be MORNING or EVENING.")


def main() -> None:
    """Show valid parsing and representative rejected input."""
    for text in (" 8.5 ", "8,5", "eight", "NaN"):
        try:
            print(f"{text!r} -> {parse_decimal(text, 'litres')}")
        except ValueError as error:
            print(f"{text!r} -> ERROR: {error}")


if __name__ == "__main__":
    main()
