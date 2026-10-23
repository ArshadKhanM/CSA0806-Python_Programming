# Task 11 — Final design recommendation

## Recommended design

- Parse money, litres, and analyser readings from strings into `Decimal`; never seed financial calculations from a float.
- Keep rate values, measurement references, bounds, and money precision in a central named-constant module.
- Validate IDs, finite values, quantity, quality bounds, and shift before calculation. Report invalid entries; do not clamp or silently substitute.
- Keep rate, payout, and aggregation functions reusable and return values rather than printing within calculations.
- Apply `ROUND_HALF_UP` to whole quality steps and to the rate/payment quantum, then sum the rounded farmer payments.
- Retain a record ledger for audit, reprints, corrections, and reconciliation. Use streaming only if the business explicitly accepts losing in-memory entry detail.
- Model the seasonal rate card as data and provide the ten-day aggregate explicitly when checking bonus eligibility.

## Complexity and scale

Rate and payment calculation is O(1) for each record. Processing n entries is O(n). A retained in-memory ledger takes O(n) space; summing into a running total takes O(1) additional space. 150,000 records are reasonable for the simple linear calculation, but production storage should be selected for audit/recovery needs rather than assumed to be in-memory.

## Alternatives and trade-offs

Integer paise is exact and efficient if every intermediate quantity is whole-paisa. A rate calculation can have sub-paisa values before its specified rounding, so a defined quantization policy is still required. Binary floats are concise but do not represent all decimal inputs exactly. Caching rates by quality pair adds O(k) storage for k unique pairs while the underlying arithmetic is already O(1); benchmark before adding it.

## Limitations and items to confirm

The brief does not specify an official half-paisa policy; this implementation chooses `ROUND_HALF_UP`. SNF 6.00–10.00 is provisional. Confirm the exact date boundaries and season mapping for April–June and whether readings should be rounded to the nearest 0.10 step or prorated. Taxes, deductions, rejected samples, duplicate IDs, analyser calibration, persistent database format, and correction/approval workflow need separate requirements.

For a real deployment, add permanent transaction IDs, database persistence, role-based access, backups, operational logs, reconciliation reports, and versioned/effective-dated rate cards. Approve a rate revision with regression tests for both season cards and range boundaries before release.

## Conclusion

The original module design should be modified rather than replaced. Decimal arithmetic, validation, pure functions, and tests remain appropriate. Seasonal configuration and the volume aggregate are localized extensions that keep the same calculation flow understandable.
