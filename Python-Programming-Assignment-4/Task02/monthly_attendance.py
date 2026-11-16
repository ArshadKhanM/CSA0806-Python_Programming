"""Aggregate daily attendance files into monthly CSV reports."""

import argparse
import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path


class InvalidAttendanceLine(ValueError):
    """A line does not match register,date,P-or-A."""


@dataclass(frozen=True)
class AttendanceError:
    file_name: str
    line_number: int
    raw_line: str
    reason: str


def parse_attendance_line(line: str, month: str) -> tuple[str, str, str]:
    fields = [field.strip() for field in line.strip().split(",")]
    if len(fields) != 3:
        raise InvalidAttendanceLine(f"expected 3 fields, found {len(fields)}")
    register, date_text, status = fields
    if not register:
        raise InvalidAttendanceLine("register number is empty")
    try:
        parsed_date = date.fromisoformat(date_text)
    except ValueError as error:
        raise InvalidAttendanceLine(f"invalid date {date_text!r}") from error
    if parsed_date.strftime("%Y-%m") != month:
        raise InvalidAttendanceLine(f"date is outside requested month {month}")
    if status not in {"P", "A"}:
        raise InvalidAttendanceLine(f"invalid status {status!r}")
    return register, date_text, status


def process_month(folder: str | Path, month: str, output_folder: str | Path) -> dict[str, object]:
    """Read each matching daily file once and write the three requested reports."""
    source_folder = Path(folder)
    output = Path(output_folder)
    output.mkdir(parents=True, exist_ok=True)
    counts: dict[str, list[int]] = {}
    errors: list[AttendanceError] = []
    input_files = sorted(source_folder.glob(f"attendance_{month}-*.csv"))
    if not source_folder.is_dir():
        errors.append(
            AttendanceError(source_folder.name, 0, "", "input folder does not exist")
        )

    for path in input_files:
        try:
            with path.open("r", encoding="utf-8", newline="") as source:
                for line_number, raw_line in enumerate(source, start=1):
                    if not raw_line.strip():
                        continue
                    try:
                        register, _, status = parse_attendance_line(raw_line, month)
                    except InvalidAttendanceLine as error:
                        errors.append(
                            AttendanceError(path.name, line_number, raw_line.rstrip("\r\n"), str(error))
                        )
                        continue
                    student_counts = counts.setdefault(register, [0, 0])
                    student_counts[0 if status == "P" else 1] += 1
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, IsADirectoryError) as error:
            errors.append(AttendanceError(path.name, 0, "", str(error)))

    with (output / "attendance_percentages.csv").open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(("register", "present", "absent", "records", "percentage"))
        for register in sorted(counts):
            present, absent = counts[register]
            total = present + absent
            writer.writerow((register, present, absent, total, f"{100 * present / total:.2f}"))

    below = [
        (register, 100 * present / (present + absent))
        for register, (present, absent) in counts.items()
        if 100 * present / (present + absent) < 75
    ]
    with (output / "below_75.csv").open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(("register", "percentage"))
        writer.writerows((register, f"{percentage:.2f}") for register, percentage in sorted(below))

    with (output / "damaged_records.csv").open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(("file", "line", "record", "error"))
        writer.writerows((item.file_name, item.line_number, item.raw_line, item.reason) for item in errors)
    return {"files": input_files, "counts": counts, "errors": errors, "below_75": below}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("daily_files"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("output"))
    parser.add_argument("--month", default="2026-10")
    args = parser.parse_args()
    result = process_month(args.input, args.month, args.output)
    print(f"files={len(result['files'])}, students={len(result['counts'])}, damaged={len(result['errors'])}")
    print(f"reports written to {args.output}")


if __name__ == "__main__":
    main()
