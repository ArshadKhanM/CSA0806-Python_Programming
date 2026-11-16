"""Main program for the three-module attendance organization."""

import tempfile
from pathlib import Path

from Task05.three_modules.reader import read_rows
from Task05.three_modules.report import write_reports
from Task05.three_modules.stats import absent_three_days, percentages


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
