# Task 1 — Problem and data analysis

## Problem statement

For each milk collection, validate a farmer identifier, litres, fat percentage, SNF percentage, and shift. Calculate a quality-based rate and a payment, record the result, and compute the ten-day payable total.

## Data dictionary

| Value | Python type | Validation / rationale |
|---|---|---|
| `farmer_id` | `str` | Required after stripping whitespace; preserve leading zeroes |
| `litres` | `Decimal` | Finite and greater than zero; fractional litres are supported |
| `fat_percent` | `Decimal` | 2.00–7.00 inclusive |
| `snf_percent` | `Decimal` | 6.00–10.00 inclusive; provisional range from reference |
| `shift` | `str` | `MORNING` or `EVENING`, case-insensitive |
| `rate_per_litre` | `Decimal` | Formula result quantized to Rs 0.01 |
| `payment` | `Decimal` | Litres × rate; quantized to nearest paisa |
| `ten_day_total` | `Decimal` | Sum of already-rounded farmer payments |
| `season` | `str` | `STANDARD` or `APR_JUN`; caller maps dates to this code |

## Rates and validation

Reference point: fat 3.5%, SNF 8.5%, base Rs 30.00/L. Each nearest 0.10% fat step changes the rate by Rs 0.40; each nearest 0.10% SNF step changes it by Rs 0.30. `Decimal` input comes from text. Half-up is used for quality steps, rates, and payments. Invalid readings are rejected, not clamped.

The SNF bounds are assumptions rather than assignment-provided official policy; ask the co-operative to confirm them. Taxes, deductions, duplicate identifiers, rejected milk, calibration and date/time-zone rules are out of scope because the brief does not specify them.

## Alternative representation and complexity

Separate variables such as `litres1`, `fat1`, `snf1` repeat fields and calculation logic. A list of structured records is easier to loop over, validate, audit, and extend. Processing n records is O(n). The Task 9 program retains the accepted ledger, requiring O(n) storage; a streaming total would use O(1) extra storage but would not retain transaction details.
