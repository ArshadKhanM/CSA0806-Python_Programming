"""Read attendance CSV rows."""

import csv
from pathlib import Path


def read_rows(path: str | Path) -> list[tuple[str, str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as source:
        return [
            (row[0].strip(), row[1].strip(), row[2].strip())
            for row in csv.reader(source)
            if row and len(row) == 3 and all(value.strip() for value in row)
        ]
