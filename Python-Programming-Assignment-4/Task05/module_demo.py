"""Run all four attendance organizations on the same sample data."""

import tempfile
from pathlib import Path

from Task05.attendance_package.main import run as package_run
from Task05.module_import.main import run as module_run
from Task05.single_script.attendance_single import run as single_run
from Task05.three_modules.main import run as three_module_run


def main() -> None:
    sample = Path(__file__).with_name("sample_attendance.csv")
    for name, run in (
        ("one script", single_run),
        ("one imported module", module_run),
        ("three modules", three_module_run),
        ("package", package_run),
    ):
        with tempfile.TemporaryDirectory() as output:
            result = run(sample, output)
        print(name, result["percentages"], result["streaks"])


if __name__ == "__main__":
    main()
