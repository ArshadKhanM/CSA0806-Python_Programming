"""Merge contacts using normalized phone numbers and dictionary indexing."""

import argparse
import random
import re
import time
from collections.abc import Iterable
from typing import Any


def normalize_phone(value: str) -> str:
    digits = "".join(character for character in value if character.isdigit())
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    return digits


def normalize_name(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def _as_values(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    return [value] if isinstance(value, str) else value


def _make_record(contact: dict[str, Any], sequence: int) -> dict[str, Any]:
    original_name = str(contact.get("name") or "").strip()
    numbers = {normalize_phone(value) for value in _as_values(contact.get("phones", contact.get("phone")))}
    numbers.discard("")
    emails = {value.strip().casefold() for value in _as_values(contact.get("emails", contact.get("email")))}
    emails.discard("")
    aliases = {original_name} if original_name else set()
    return {
        "name": original_name,
        "normalized_name": normalize_name(original_name),
        "names": aliases,
        "numbers": numbers,
        "emails": emails,
        "first_seen": sequence,
    }


def merge_contacts(contacts: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge transitive matches with union-find and a number-to-record index."""
    parent: list[int] = []
    component_size: list[int] = []
    records: list[dict[str, Any]] = []
    phone_index: dict[str, int] = {}

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(first: int, second: int) -> int:
        root_a, root_b = find(first), find(second)
        if root_a == root_b:
            return root_a
        if component_size[root_a] < component_size[root_b]:
            root_a, root_b = root_b, root_a
        parent[root_b] = root_a
        component_size[root_a] += component_size[root_b]
        target, source = records[root_a], records[root_b]
        target_first_seen = target["first_seen"]
        source_first_seen = source["first_seen"]
        target["numbers"].update(source["numbers"])
        target["emails"].update(source["emails"])
        target["names"].update(source["names"])
        target["first_seen"] = min(target_first_seen, source_first_seen)
        if not target["name"] or (source["name"] and source_first_seen < target_first_seen):
            target["name"] = source["name"]
            target["normalized_name"] = source["normalized_name"]
        return root_a

    for sequence, contact in enumerate(contacts):
        record = _make_record(contact, sequence)
        item = len(records)
        records.append(record)
        parent.append(item)
        component_size.append(1)
        matched_roots = {
            find(phone_index[number])
            for number in record["numbers"]
            if number in phone_index
        }
        for root in matched_roots:
            item = union(item, root)
        root = find(item)
        records[root]["numbers"].update(record["numbers"])
        records[root]["emails"].update(record["emails"])
        records[root]["names"].update(record["names"])
        if not records[root]["name"] and record["name"]:
            records[root]["name"] = record["name"]
            records[root]["normalized_name"] = record["normalized_name"]
        for number in records[root]["numbers"]:
            phone_index[number] = root

    merged = []
    for index, record in enumerate(records):
        if find(index) != index:
            continue
        merged.append(
            {
                "name": record["name"],
                "names": sorted(record["names"], key=lambda value: (value.casefold(), value)),
                "numbers": sorted(record["numbers"]),
                "emails": sorted(record["emails"]),
                "first_seen": record["first_seen"],
            }
        )
    return sorted(merged, key=lambda item: item["first_seen"])


def merge_contacts_pairwise(contacts: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Simple O(n^2) baseline for comparison on small input sizes."""
    merged: list[dict[str, Any]] = []
    for sequence, contact in enumerate(contacts):
        incoming = _make_record(contact, sequence)
        matches = [record for record in merged if record["numbers"] & incoming["numbers"]]
        if not matches:
            merged.append(incoming)
            continue
        target = matches[0]
        for extra in matches[1:]:
            target["numbers"].update(extra["numbers"])
            target["emails"].update(extra["emails"])
            target["names"].update(extra["names"])
            merged.remove(extra)
        target["numbers"].update(incoming["numbers"])
        target["emails"].update(incoming["emails"])
        target["names"].update(incoming["names"])
        if not target["name"] and incoming["name"]:
            target["name"] = incoming["name"]
        target["first_seen"] = min(target["first_seen"], sequence)
    return [
        {
            "name": record["name"],
            "names": sorted(record["names"], key=lambda value: (value.casefold(), value)),
            "numbers": sorted(record["numbers"]),
            "emails": sorted(record["emails"]),
            "first_seen": record["first_seen"],
        }
        for record in merged
    ]


def generate_contacts(count: int, seed: int = 7) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    contacts = []
    for index in range(count):
        person = index // 2
        local_number = f"98400{person:05d}"
        phone = f"+91 {local_number[:5]} {local_number[5:]}" if index % 2 else local_number
        contacts.append(
            {
                "name": f"Person {person}" if index % 2 == 0 else f"person {person}",
                "phones": [phone],
                "emails": [f"person{person}@example.com"] if rng.random() < 0.8 else [],
            }
        )
    return contacts


def benchmark(sizes: tuple[int, ...] = (1_000, 100_000)) -> None:
    for size in sizes:
        contacts = generate_contacts(size)
        start = time.perf_counter()
        indexed = merge_contacts(contacts)
        indexed_time = time.perf_counter() - start
        if size <= 1_000:
            start = time.perf_counter()
            pairwise = merge_contacts_pairwise(contacts)
            pairwise_time = time.perf_counter() - start
            if indexed != pairwise:
                raise AssertionError("dictionary and pairwise merges disagree")
            pairwise_display = f"{pairwise_time:.6f}s"
        else:
            pairwise_display = f"not run (about {size * size:,} pair comparisons)"
        print(
            f"{size:>7} contacts: indexed={indexed_time:.6f}s, "
            f"pairwise={pairwise_display}, merged={len(indexed)}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()
    contacts = [
        {"name": "Dr. Ravi", "phones": ["+91 98400 12345"], "emails": ["Ravi@example.com"]},
        {"name": "ravi kumar", "phones": ["9840012345"], "emails": ["ravi@example.com"]},
        {"name": "Mina", "phones": ["9000011111"], "emails": []},
        {"name": "Ravi", "phones": ["9840012345", "9000011111"], "emails": ["other@example.com"]},
        {"name": "No phone", "phones": [], "emails": ["none@example.com"]},
    ]
    print("merged:", merge_contacts(contacts))
    print("normalised number:", normalize_phone("+91 98400 12345"))
    if args.benchmark:
        benchmark()


if __name__ == "__main__":
    main()
