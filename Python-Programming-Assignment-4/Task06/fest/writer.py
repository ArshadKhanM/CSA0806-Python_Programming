"""Write the fest master list, event lists, summary, and error log."""

import csv
import re
from pathlib import Path
from collections.abc import Mapping

from .models import Registration, RejectedRecord


def _event_slug(event: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", event.casefold()).strip("-")
    return slug or "unnamed"


def write_outputs(
    master: Mapping[str, Registration],
    errors: list[RejectedRecord],
    duplicates: int,
    output_dir: str | Path,
) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    master_path = output / "master.csv"
    with master_path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(("register", "name", "department", "email", "events"))
        for register in sorted(master):
            entry = master[register]
            writer.writerow(
                (register, entry.name, entry.department, entry.email, ";".join(sorted(entry.events)))
            )

    events = sorted({event for entry in master.values() for event in entry.events})
    event_paths: dict[str, Path] = {}
    for event in events:
        path = output / f"event_{_event_slug(event)}.csv"
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.writer(target)
            writer.writerow(("register", "name", "department", "email"))
            for register in sorted(master):
                entry = master[register]
                if event in entry.events:
                    writer.writerow((register, entry.name, entry.department, entry.email))
        event_paths[event] = path

    summary_path = output / "summary.txt"
    summary_path.write_text(
        f"unique registrations: {len(master)}\n"
        f"duplicate registrations merged: {duplicates}\n"
        f"event categories: {len(events)}\n"
        f"rejected records: {len(errors)}\n",
        encoding="utf-8",
    )
    error_path = output / "errors.log"
    with error_path.open("w", encoding="utf-8") as target:
        for item in errors:
            target.write(
                f"{item.file_name}:{item.line_number}: {item.reason}"
                + (f" | {item.raw_line}" if item.raw_line else "")
                + "\n"
            )
    return {"master": master_path, "summary": summary_path, "errors": error_path, **event_paths}
