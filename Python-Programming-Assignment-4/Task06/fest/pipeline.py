"""Coordinate input, validation, deduplication, and report creation."""

from pathlib import Path
from collections.abc import Iterable

from .merge import merge_registrations
from .models import RejectedRecord, Registration
from .reader import read_department_file
from .writer import write_outputs


def process_files(
    input_files: Iterable[str | Path], output_dir: str | Path
) -> dict[str, object]:
    registrations: list[Registration] = []
    errors: list[RejectedRecord] = []
    for path in input_files:
        parsed, rejected = read_department_file(path)
        registrations.extend(parsed)
        errors.extend(rejected)
    master, duplicates = merge_registrations(registrations)
    outputs = write_outputs(master, errors, duplicates, output_dir)
    return {
        "master": master,
        "errors": errors,
        "duplicates": duplicates,
        "outputs": outputs,
    }


def process_department_folder(
    input_dir: str | Path, output_dir: str | Path, department_count: int = 5
) -> dict[str, object]:
    source = Path(input_dir)
    paths = [source / f"department_{number:02d}.csv" for number in range(1, department_count + 1)]
    return process_files(paths, output_dir)
