"""Named constants for the original milk payment calculation."""

from decimal import Decimal

BASE_RATE = Decimal("30.00")
FAT_REFERENCE = Decimal("3.50")
SNF_REFERENCE = Decimal("8.50")
FAT_STEP = Decimal("0.10")
SNF_STEP = Decimal("0.10")
FAT_STEP_VALUE = Decimal("0.40")
SNF_STEP_VALUE = Decimal("0.30")
MIN_FAT = Decimal("2.00")
MAX_FAT = Decimal("7.00")
# Provisional validation assumption; confirm this range with the co-operative.
MIN_SNF = Decimal("6.00")
MAX_SNF = Decimal("10.00")
CENT = Decimal("0.01")
ONE = Decimal("1")
ALLOWED_SHIFTS = frozenset({"MORNING", "EVENING"})
