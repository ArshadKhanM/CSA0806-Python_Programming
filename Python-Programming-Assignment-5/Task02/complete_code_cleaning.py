"""Completed B1 CSV and min-max normalization example."""

import csv
import io

RAW = """station,date,pm25
Adyar,2026-10-01,48
Adyar,2026-10-02,NA
Adyar,2026-10-03,
Guindy,2026-10-01,95
Guindy,2026-10-02,-5
Guindy,2026-10-03,121
Faulty,2026-10-01,1200"""


def load_clean(text):
    """Return station/date/value rows with missing and implausible values removed."""
    rows = []
    for row in csv.DictReader(io.StringIO(text)):
        raw_value = (row.get("pm25") or "").strip()
        if not raw_value or raw_value.upper() == "NA":
            continue
        value = float(raw_value)
        if 0 <= value <= 999:
            rows.append((row["station"], row["date"], value))
    return rows


def min_max(values):
    """Scale values to [0, 1], rounded to three decimal places."""
    if not values:
        return []
    minimum = min(values)
    maximum = max(values)
    if minimum == maximum:
        return [0.0 for _ in values]
    return [round((value - minimum) / (maximum - minimum), 3) for value in values]


if __name__ == "__main__":
    clean = load_clean(RAW)
    print(clean)
    print(min_max([pm for _, _, pm in clean]))
