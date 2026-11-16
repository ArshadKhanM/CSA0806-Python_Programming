"""Write the two attendance reports."""

import csv
from pathlib import Path

from .stats import absent_three_days, percentages


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
