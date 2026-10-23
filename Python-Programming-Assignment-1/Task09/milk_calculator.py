"""Validated milk collection payment calculator."""

import argparse
from dataclasses import dataclass
from decimal import Decimal

from Task05.input_validation import parse_decimal, validate_entry
from Task07.milkrate import payout, rate_per_litre, ten_day_total


@dataclass(frozen=True)
class Collection:
    """One validated farmer collection and its calculated payment."""

    farmer_id: str
    litres: Decimal
    fat: Decimal
    snf: Decimal
    shift: str
    rate: Decimal
    payment: Decimal


def calculate_entry(
    farmer_id: str,
    litres: Decimal,
    fat: Decimal,
    snf: Decimal,
    shift: str,
) -> Collection:
    """Validate and calculate one collection record."""
    validate_entry(farmer_id, litres, fat, snf, shift)
    rate = rate_per_litre(fat, snf)
    payment = payout(litres, fat, snf)
    return Collection(farmer_id.strip(), litres, fat, snf, shift.strip().upper(), rate, payment)


def demo() -> list[Collection]:
    """Return the five deterministic examples used in the assignment."""
    raw_entries = (
        ("F001", "10", "3.5", "8.5", "MORNING"),
        ("F002", "8.5", "4.2", "8.7", "EVENING"),
        ("F003", "12", "3.1", "8.3", "MORNING"),
        ("F004", "1", "2.0", "8.5", "EVENING"),
        ("F005", "1", "7.0", "8.5", "MORNING"),
    )
    return [
        calculate_entry(
            farmer_id,
            parse_decimal(litres, "litres"),
            parse_decimal(fat, "fat"),
            parse_decimal(snf, "SNF"),
            shift,
        )
        for farmer_id, litres, fat, snf, shift in raw_entries
    ]


def run_interactive() -> None:
    """Read entries until a blank farmer ID is entered."""
    ledger: list[Collection] = []
    while True:
        farmer_id = input("Farmer ID (blank to finish): ").strip()
        if not farmer_id:
            break
        try:
            litres = parse_decimal(input("Litres: "), "litres")
            fat = parse_decimal(input("Fat percentage: "), "fat")
            snf = parse_decimal(input("SNF percentage: "), "SNF")
            shift = input("Shift (MORNING/EVENING): ")
            ledger.append(calculate_entry(farmer_id, litres, fat, snf, shift))
        except ValueError as error:
            print(f"Entry rejected: {error}")

    print_ledger(ledger)


def print_ledger(ledger: list[Collection]) -> None:
    """Display accepted entries and the rounded ten-day total."""
    print("Farmer | Shift | Litres | Fat | SNF | Rate/L | Payment")
    for entry in ledger:
        print(
            f"{entry.farmer_id} | {entry.shift} | {entry.litres} | "
            f"{entry.fat} | {entry.snf} | Rs {entry.rate:.2f} | "
            f"Rs {entry.payment:.2f}"
        )
    print(f"Ten-day total: Rs {ten_day_total([entry.payment for entry in ledger]):.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--demo",
        action="store_true",
        help="calculate the five assignment examples instead of prompting",
    )
    args = parser.parse_args()
    if args.demo:
        print_ledger(demo())
    else:
        run_interactive()


if __name__ == "__main__":
    main()
