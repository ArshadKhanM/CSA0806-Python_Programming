"""Main program using the attendance package."""

import tempfile
from pathlib import Path

from Task05.attendance_package.attendance import (
    absent_three_days,
    percentages,
    read_rows,
    write_reports,
)


def run(input_file: str | Path, output_dir: str | Path) -> dict[str, object]:
    rows = read_rows(input_file)
    write_reports(rows, output_dir)
    return {"rows": rows, "percentages": percentages(rows), "streaks": absent_three_days(rows)}


def main() -> None:
    sample = Path(__file__).parents[1] / "sample_attendance.csv"
    with tempfile.TemporaryDirectory() as output:
        print(run(sample, output))


if __name__ == "__main__":
    main()
