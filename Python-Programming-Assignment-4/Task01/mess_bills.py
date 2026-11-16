"""Stream mess-bill records and collect malformed rows for review."""

import csv
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path


class InvalidMessRecord(ValueError):
    """A non-empty mess-bill line is missing or has invalid fields."""


@dataclass(frozen=True)
class RejectedLine:
    line_number: int
    content: str
    reason: str


@dataclass(frozen=True)
class MessBillResult:
    total: Decimal
    report_lines: list[str]
    rejected: list[RejectedLine]


def process_mess_file(file_name: str | Path) -> MessBillResult:
    """Process one CSV-like line per student without loading the file at once."""
    total = Decimal("0.00")
    report_lines: list[str] = []
    rejected: list[RejectedLine] = []

    with open(file_name, "r", encoding="utf-8", newline="") as source:
        for line_number, raw_line in enumerate(source, start=1):
            if not raw_line.strip():
                continue
            try:
                fields = next(csv.reader([raw_line]))
                if len(fields) != 3:
                    raise InvalidMessRecord(f"expected 3 fields, found {len(fields)}")
                register, name, amount_text = (field.strip() for field in fields)
                if not register or not name:
                    raise InvalidMessRecord("register number and name are required")
                amount = Decimal(amount_text)
                if not amount.is_finite() or amount < 0:
                    raise InvalidMessRecord("amount must be a non-negative finite value")
            except (csv.Error, InvalidMessRecord, InvalidOperation) as error:
                rejected.append(RejectedLine(line_number, raw_line.rstrip("\r\n"), str(error)))
                continue
            total += amount
            report_lines.append(f"{register}, {name}, {amount:.2f}")

    return MessBillResult(total, report_lines, rejected)


def main(argv: list[str] | None = None) -> int:
    arguments = argv if argv is not None else sys.argv[1:]
    file_name = arguments[0] if arguments else str(Path(__file__).with_name("mess_oct.csv"))
    try:
        result = process_mess_file(file_name)
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, IsADirectoryError) as error:
        print(f"Could not process {file_name}: {error}", file=sys.stderr)
        return 1
    print("\n".join(result.report_lines))
    print(f"Total {result.total:.2f}")
    print("Rejected:", result.rejected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
