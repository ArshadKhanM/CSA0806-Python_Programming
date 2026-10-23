# Python Programming Assignment 1

## Design, Implement and Validate a Payment Calculator for a Village Milk Co-operative

**Student name:** `Mohamed Arshad Khan M`

**Register number:** `1965L260001`

**Course:** Python Programming

**Python used for validation:** 3.11.0; standard library only

> **Identity and source note:** The example student's identifying details in the reference PDF have intentionally not been copied. Replace the placeholders with your own details before submission. The provided reference PDF remains unmodified in the project root.

## Summary

This submission completes all twelve assignment tasks. It models milk collection entries as records, parses numeric input as `Decimal`, validates before calculation, computes rate and farmer payment with an explicit `ROUND_HALF_UP` policy, and sums already-rounded farmer payments. Task 12 extends the design with separate seasonal cards and a bonus of Rs 0.50/L only when the farmer's ten-day volume is **greater than** 500 L.

## Assumptions and interpretation of the brief

1. The reference rate is Rs 30.00/L at fat 3.5% and SNF 8.5%.
2. Each nearest 0.10 percentage-point fat step changes rate by Rs 0.40; each nearest 0.10 percentage-point SNF step changes it by Rs 0.30.
3. The original brief does not specify half-step rounding. This solution explicitly uses `Decimal` `ROUND_HALF_UP` for quality-step counts, rate, and payable amounts.
4. Fat is accepted inclusively from 2.00% through 7.00%. SNF is provisionally accepted from 6.00% through 10.00%, exactly as the reference's stated assumption; the co-operative/instructor must confirm it.
5. Litres must be finite and greater than zero. Farmer ID must be non-empty, and shift must be `MORNING` or `EVENING` (case-insensitive).
6. Ten-day payable total is the sum of individual farmer payments after each is rounded to the nearest paisa. No taxes, deductions, penalties, duplicate-ID policy, or milk rejection rules were supplied.
7. For Task 12, the April–June card changes base rate to Rs 32.00 and fat-step value to Rs 0.45. Reference values, step size, and SNF-step value remain unchanged because the change request did not say they changed.
8. Analyser values with two decimal places are quantized to the nearest 0.10 percentage-point step using `ROUND_HALF_UP`; the brief's revised precision does not state a proration alternative.
9. Bonus eligibility is based on the farmer's aggregated ten-day litres. Exactly 500 L receives no bonus; only a total above 500 L does.
10. “April–June” is represented by the explicit `APR_JUN` season code; all other dates/seasons must be designated `STANDARD` by the caller. The brief does not define timezone or date-boundary handling.
11. The reference PDF lists Rs 16,275.50 for its 501 L challenge case, but its own stated formula gives 501 × (Rs 32.00 + Rs 0.50) = **Rs 16,282.50**. This submission follows the stated formula and records the discrepancy rather than reproducing an arithmetically inconsistent expected result.

## Formula and money policy

For each entry, with `D = Decimal`:

```text
fat_steps = ROUND_HALF_UP((fat - 3.5) / 0.1)
snf_steps = ROUND_HALF_UP((snf - 8.5) / 0.1)
rate = 30.00 + (fat_steps × 0.40) + (snf_steps × 0.30)
rate_per_litre = rate rounded to Rs 0.01 using ROUND_HALF_UP
payment = (litres × rate_per_litre) rounded to Rs 0.01 using ROUND_HALF_UP
ten_day_total = sum of rounded farmer payments
```

For Task 12, replace base and fat increment with the selected season card, and use `rate + 0.50` per litre if the ten-day volume is greater than 500 L. Inputs originate as strings; no financial calculation constructs `Decimal` from a binary float.

## Task 1 — Problem and data analysis (4 marks)

The calculator receives one record per farmer collection and produces a rate, payable amount, and ten-day total.

| Field | Type | Validation / reason |
|---|---|---|
| Farmer ID | `str` | Required, non-whitespace; identifiers may contain leading zeroes |
| Litres | `Decimal` | Finite and strictly positive; may be fractional |
| Fat % | `Decimal` | Inclusive 2.00–7.00 |
| SNF % | `Decimal` | Inclusive 6.00–10.00 (provisional assumption) |
| Shift | `str` | `MORNING` or `EVENING` |
| Rate, payment, total | `Decimal` | Rate/payment quantized to 0.01; total sums rounded payments |
| Season / date | explicit season code | `STANDARD` or `APR_JUN`; date mapping belongs to the caller |

The detailed data analysis and rejected alternatives are in [`../Task01/analysis.md`](../Task01/analysis.md). Processing is O(n) time for n entries. Storing an audit ledger is O(n) space; a running total alone is O(1) extra space.

## Task 2 — Values, types, and exact money (4 marks)

Python's `int`, `float`, `str`, `bool`, and `list` values have distinct types. `/` performs true division, `//` floors (so `-7 // 2 == -4`), and `%` returns a remainder. Binary float cannot exactly represent many decimal fractions: `0.1 + 0.2 == 0.3` is false. `Decimal` constructed from strings and integer paise both avoid that representation issue; this project uses `Decimal` for readable financial arithmetic.

The program in [`../Task02/decimal_total.py`](../Task02/decimal_total.py) runs the interpreter examples and compares summation of 1,000 string payments of Rs 33.40 plus three Rs 0.10 entries. Exact expected result is Rs 33,400.30 (3,340,030 paise). The actual run is captured in [`../Task02/interpreter_session.txt`](../Task02/interpreter_session.txt). Floating-point display can vary by Python/platform; it is shown as a contrast, not used for payment.

Time is O(n) and accumulator space is O(1).

## Task 3 — Variables and constants (3 marks)

[`../Task03/constants.py`](../Task03/constants.py) names the rate, reference measurements, step sizes and values, rounding quantum, and allowed bounds. Variables and functions use `snake_case`; constants use `UPPER_CASE`. Python permits rebinding a variable to a different type, but descriptive names and one central source of constants reduce accidental inconsistency. A small rate card takes O(1) space and lookup/calculation is O(1) per entry.

## Task 4 — Expressions and rounding (4 marks)

[`../Task04/expressions.py`](../Task04/expressions.py) implements signed step calculation and quantization. It avoids float expressions such as `(4.2 - 3.5) / 0.1`, whose binary approximation can land slightly off the intended integer. `ROUND_HALF_UP` is explicit, in contrast to Python's built-in `round()` ties-to-even behavior. Parentheses make operator order clear; comparisons use inclusive range checks. Each individual rate or payment expression uses O(1) time and O(1) extra space.

## Task 5 — Input and validation (3 marks)

[`../Task05/input_validation.py`](../Task05/input_validation.py) strips whitespace, converts from decimal text, rejects malformed/non-finite values, and validates ID, litres, fat, SNF, and shift before calculation. Errors explain the rejected field rather than clamping values or guessing locale. For example, `" 8.5 "` is accepted while `"8,5"`, `"eight"`, NaN, and infinity are rejected. Parsing and validation are O(1) for normal-sized inputs.

## Task 6 — Functions and scope (4 marks)

[`../Task06/payment_functions.py`](../Task06/payment_functions.py) separates rate calculation, payout, and ten-day aggregation into reusable functions. Functions return values instead of printing as a side effect. Their dependencies are passed/imported explicitly; calculation does not mutate global rates. Each rate/payout is O(1), and aggregation over n payment values is O(n) time and O(1) additional space.

## Task 7 — Module design (4 marks)

[`../Task07/milkrate.py`](../Task07/milkrate.py) provides the reusable Task 7 API and a guarded demonstration. The demonstration runs only when invoked as a module; importing it has no console side effect. [`../Task07/test_milkrate.py`](../Task07/test_milkrate.py) checks rates, payments, totals, and invalid inputs. From the project root, use `python -m Task07.milkrate`; package imports are designed for root-based execution.

## Task 8 — Algorithm, pseudocode, and flowchart (4 marks)

The full pseudocode is in [`../Task08/pseudocode.txt`](../Task08/pseudocode.txt), and Mermaid source for the validation/calculation flow is in [`../Task08/flowchart.mmd`](../Task08/flowchart.mmd).

```text
SET total to 0.00
FOR each collection record:
    parse decimal text
    validate ID, finite numeric values, positive litres, quality ranges, and shift
    if invalid: report the validation error and continue
    calculate fat and SNF step counts with Decimal ROUND_HALF_UP
    calculate and quantize rate to 0.01
    calculate and quantize payment to 0.01
    retain the record and add its payment to total
DISPLAY the accepted ledger, rejected-entry errors, and total
```

The calculator validates each collection independently and reports errors to the user. For accepted records it retains an in-memory audit-friendly ledger. The loop is O(n); storage is O(n) because the ledger is retained.

## Task 9 — Implementation and test plan (4 marks)

The runnable application is [`../Task09/milk_calculator.py`](../Task09/milk_calculator.py). Run the included example collection with `python -m Task09.milk_calculator --demo`, or run interactively with `python -m Task09.milk_calculator`. The input flow can accept multiple entries and then computes a rounded total. Automated tests are in [`../Task09/test_milk_calculator.py`](../Task09/test_milk_calculator.py).

| Case | Input | Expected | Purpose |
|---|---|---:|---|
| T1 | 10 L; fat 3.5; SNF 8.5 | Rs 300.00 | Reference rate |
| T2 | 8.5 L; fat 4.2; SNF 8.7 | Rs 283.90 | Above reference |
| T3 | 12 L; fat 3.1; SNF 8.3 | Rs 333.60 | Below reference |
| T4 | 1 L; fat 2.0; SNF 8.5 | Rs 24.00 | Minimum fat |
| T5 | 1 L; fat 7.0; SNF 8.5 | Rs 44.00 | Maximum fat |
| T6 | -1 L | `ValueError` | Non-positive amount |
| T7 | Fat 7.1 | `ValueError` | Out-of-range quality |
| T8 | Litres `"eight"` | `ValueError` | Invalid decimal text |
| T9 | 1 L; reference quality | Rs 30.00 | Reference boundary |

The first five payments sum to Rs 985.50. [`../Task09/test_results.txt`](../Task09/test_results.txt) contains captured execution evidence; the test suite is O(m) for m test cases.

## Task 10 — Expected/executed results and benchmark (4 marks)

[`../Task10/benchmark.py`](../Task10/benchmark.py) compares summing float conversions against Decimal values constructed from strings. For N base entries at Rs 33.40 plus three Rs 0.10 adjustments, exact totals are:

| N | Exact Decimal total | Observed float total | Observed float-minus-Decimal | Float elapsed (s) | Decimal elapsed (s) |
|---:|---:|---:|---:|---:|---:|
| 300 | Rs 10,020.30 | 10020.299999999945 | -5.5E-11 | 0.000044 | 0.000139 |
| 6,000 | Rs 200,400.30 | 200400.29999997854 | -2.146E-8 | 0.001002 | 0.002521 |
| 150,000 | Rs 5,010,000.30 | 5010000.300000842 | 8.42E-7 | 0.025504 | 0.062577 |

These are actual single-run measurements from Python 3.11.0 on this machine; they are not portable performance guarantees. The full console output is recorded in [`../Task10/benchmark_results.txt`](../Task10/benchmark_results.txt). Timings depend on machine load and runtime. Decimal and float both require O(n) time; the benchmark adds O(n) storage for the generated input list. The payment calculator itself need not use the benchmark's float path.

## Task 11 — Final design recommendation (4 marks)

Use string-to-Decimal parsing, a single source of named rate constants, strict validation, pure calculation functions, per-farmer half-up rounding, and an audit ledger. The detailed rationale, limitations, and rate-revision process are in [`../Task11/recommendation.md`](../Task11/recommendation.md). For production at 150,000 records, calculation remains O(n); persistent transaction storage, reconciliation, access controls, backups, and operational logging should be selected based on co-operative requirements.

Limitations include the unconfirmed SNF range and rounding policy, no date/time-zone mapping for the seasonal card, and no requirements for taxes, rejected milk, duplicate IDs, or permanent ledger storage.

## Task 12 — Seasonal rates and volume bonus (8 marks)

[`../Task12/seasonal_milkrate.py`](../Task12/seasonal_milkrate.py) retains the core module design and adds `STANDARD` and `APR_JUN` cards, two-decimal quality input, and a Rs 0.50/L bonus based on aggregated ten-day volume. Season names are validated rather than silently defaulted. The module rejects a ten-day aggregate smaller than the current collection amount.

| Case | Inputs | Expected |
|---|---|---:|
| C1 | Standard; fat 3.56, SNF 8.50 | Rs 30.40/L |
| C2 | April–June; fat 3.56, SNF 8.50 | Rs 32.45/L |
| C3 | April–June; 520 L, reference quality, total 520 L | Rs 16,900.00 |
| C4 | April–June; 500 L, reference quality, total 500 L | Rs 16,000.00; no bonus |
| C5 | April–June; 501 L, reference quality, total 501 L | Rs 16,282.50 (formula-derived; reference PDF's Rs 16,275.50 is inconsistent) |

The test suite additionally checks step rounding, invalid season, validation bounds, and invalid volume. Actual console evidence is in [`../Task12/challenge_tests.txt`](../Task12/challenge_tests.txt). This is a modification rather than a redesign: rate cards vary by season, while validation, Decimal calculations, and module boundaries remain. Calculation is O(1) per entry; ten-day aggregation from a collection list is O(n).

## Conclusion

The completed implementation follows the assignment's ordering and provides executable examples, tests, report, algorithm artifacts, and captured benchmark/test outputs. The core safeguards are exact decimal input, explicit rounding, strict validation, a retained record ledger, and tested seasonal bonus boundaries. Before submission, replace student placeholders, confirm policy assumptions, rerun tests/benchmark on the target machine, and update the real GitHub URL after publishing.

## PDF export

No PDF generation package was available in the initial environment, and the project intentionally has no third-party dependency. Export this Markdown report to PDF using a Markdown editor's **Export/Print to PDF** feature.
