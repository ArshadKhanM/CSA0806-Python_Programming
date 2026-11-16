"""Deduplicate registrations by register number and merge their event sets."""

from collections.abc import Iterable

from .models import Registration


def merge_registrations(
    registrations: Iterable[Registration],
) -> tuple[dict[str, Registration], int]:
    master: dict[str, Registration] = {}
    duplicates = 0
    for incoming in registrations:
        existing = master.get(incoming.register)
        if existing is None:
            master[incoming.register] = incoming
            continue
        duplicates += 1
        existing.events.update(incoming.events)
        if not existing.name:
            existing.name = incoming.name
        if not existing.department:
            existing.department = incoming.department
        if not existing.email:
            existing.email = incoming.email
    return master, duplicates
