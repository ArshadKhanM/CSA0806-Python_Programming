"""Attendance parser with a custom error and explicit file failure handling."""

import argparse
import sys
from pathlib import Path


class InvalidRecord(Exception):
    """Raised when an attendance row does not match the expected format."""


class AttendanceFileError(Exception):
    """A file could not be read as an attendance source."""


def parse_line(line: str) -> tuple[str, str, str]:
    """Parse 'register,date,P-or-A' into a validated tuple."""
    parts = [part.strip() for part in line.strip().split(",")]
    if len(parts) != 3:
        raise InvalidRecord(f"expected 3 fields, found {len(parts)}")
    register, day, status = parts
    if not register:
        raise InvalidRecord("register number is empty")
    if status not in {"P", "A"}:
        raise InvalidRecord(f"invalid status {status!r}")
    return register, day, status


def summarise(path: str | Path) -> tuple[int, int, list[tuple[int, str]]]:
    present, absent = 0, 0
    errors: list[tuple[int, str]] = []
    handle = None
    try:
        handle = Path(path).open("r", encoding="utf-8")
        with handle as source:
            for line_number, line in enumerate(source, start=1):
                try:
                    _, _, status = parse_line(line)
                except InvalidRecord as error:
                    errors.append((line_number, str(error)))
                    continue
                if status == "P":
                    present += 1
                else:
                    absent += 1
    except FileNotFoundError as error:
        raise AttendanceFileError(f"attendance file not found: {path}") from error
    except PermissionError as error:
        raise AttendanceFileError(f"permission denied: {path}") from error
    except UnicodeDecodeError as error:
        raise AttendanceFileError(f"attendance file is not valid UTF-8: {path}") from error
    else:
        return present, absent, errors
    finally:
        if handle is not None and not handle.closed:
            handle.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", default=str(Path(__file__).with_name("attendance.csv")))
    args = parser.parse_args()
    try:
        result = summarise(args.file)
    except AttendanceFileError as error:
        print(error, file=sys.stderr)
        if error.__cause__ is not None:
            print(f"caused by: {type(error.__cause__).__name__}", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
