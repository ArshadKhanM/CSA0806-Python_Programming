"""Read department files one line at a time."""

from pathlib import Path

from .models import RejectedRecord, Registration
from .validation import InvalidRegistration, parse_registration


def read_department_file(path: str | Path) -> tuple[list[Registration], list[RejectedRecord]]:
    """Return parsed registrations and invalid rows from one UTF-8 input."""
    source_path = Path(path)
    registrations: list[Registration] = []
    errors: list[RejectedRecord] = []
    try:
        with source_path.open("r", encoding="utf-8") as source:
            for line_number, raw_line in enumerate(source, start=1):
                if not raw_line.strip():
                    continue
                try:
                    registrations.append(parse_registration(raw_line))
                except InvalidRegistration as error:
                    errors.append(
                        RejectedRecord(
                            source_path.name, line_number, raw_line.rstrip("\r\n"), str(error)
                        )
                    )
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, IsADirectoryError) as error:
        detail = getattr(error, "strerror", None) or str(error)
        errors.append(
            RejectedRecord(source_path.name, 0, "", f"{type(error).__name__}: {detail}")
        )
    return registrations, errors
