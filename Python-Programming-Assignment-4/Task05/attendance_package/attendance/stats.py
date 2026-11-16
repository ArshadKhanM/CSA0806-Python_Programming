"""Attendance percentages and consecutive-absence statistics."""

from datetime import date


def percentages(rows: list[tuple[str, str, str]]) -> dict[str, float]:
    counts: dict[str, list[int]] = {}
    for register, _, status in rows:
        pair = counts.setdefault(register, [0, 0])
        pair[0 if status == "P" else 1] += 1
    return {key: pair[0] * 100 / sum(pair) for key, pair in counts.items()}


def absent_three_days(rows: list[tuple[str, str, str]]) -> list[str]:
    absent: dict[str, set[date]] = {}
    for register, day_text, status in rows:
        if status == "A":
            absent.setdefault(register, set()).add(date.fromisoformat(day_text))
    return sorted(
        register
        for register, days in absent.items()
        if any(
            day.fromordinal(day.toordinal() + 1) in days
            and day.fromordinal(day.toordinal() + 2) in days
            for day in days
        )
    )
