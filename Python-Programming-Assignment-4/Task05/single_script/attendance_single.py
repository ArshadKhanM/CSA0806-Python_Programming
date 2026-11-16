"""All attendance reading, statistics, and report writing in one script."""

import csv
import tempfile
from datetime import date
from pathlib import Path


def read_rows(path: str | Path) -> list[tuple[str, str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as source:
        return [
            (row[0].strip(), row[1].strip(), row[2].strip())
            for row in csv.reader(source)
            if row and len(row) == 3 and all(value.strip() for value in row)
        ]


def percentages(rows: list[tuple[str, str, str]]) -> dict[str, float]:
    totals: dict[str, list[int]] = {}
    for register, _, status in rows:
        counts = totals.setdefault(register, [0, 0])
        counts[0 if status == "P" else 1] += 1
    return {
        register: present * 100 / (present + absent)
        for register, (present, absent) in totals.items()
    }


def absent_three_days(rows: list[tuple[str, str, str]]) -> list[str]:
    dates: dict[str, set[date]] = {}
    for register, day_text, status in rows:
        if status == "A":
            dates.setdefault(register, set()).add(date.fromisoformat(day_text))
    return sorted(
        register
        for register, days in dates.items()
        if any(
            day.fromordinal(day.toordinal() + 1) in days
            and day.fromordinal(day.toordinal() + 2) in days
            for day in days
        )
    )


def write_reports(rows: list[tuple[str, str, str]], output_dir: str | Path) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    with (output / "percentages.csv").open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(("register", "percentage"))
        writer.writerows((key, f"{value:.2f}") for key, value in sorted(percentages(rows).items()))
    (output / "three_day_absences.txt").write_text(
        "\n".join(absent_three_days(rows)) + "\n", encoding="utf-8"
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
