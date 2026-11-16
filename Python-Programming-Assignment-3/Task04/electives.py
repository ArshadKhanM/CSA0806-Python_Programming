"""Set operations and membership measurements for elective registration."""

import argparse
import time


def clash_report(
    first: set[str], second: set[str], all_students: set[str]
) -> tuple[list[str], list[str], list[str]]:
    both = first & second
    exactly_one = first ^ second
    neither = all_students - (first | second)
    return sorted(both), sorted(exactly_one), sorted(neither)


def clash_report_methods(
    first: set[str], second: set[str], all_students: set[str]
) -> tuple[list[str], list[str], list[str]]:
    both = first.intersection(second)
    exactly_one = first.symmetric_difference(second)
    neither = all_students.difference(first.union(second))
    return sorted(both), sorted(exactly_one), sorted(neither)


def nested_clashes(first: list[str], second: list[str]) -> set[str]:
    return {student for student in first for other in second if student == other}


def benchmark(sizes: tuple[int, ...] = (10_000, 100_000, 1_000_000)) -> None:
    for size in sizes:
        values = [str(value) for value in range(size)]
        registrations = set(values)
        target = values[-1]
        repetitions = max(1, min(20, 1_000_000 // size))
        start = time.perf_counter()
        for _ in range(repetitions):
            target in values
        list_time = (time.perf_counter() - start) / repetitions
        start = time.perf_counter()
        for _ in range(repetitions):
            target in registrations
        set_time = (time.perf_counter() - start) / repetitions
        sample = min(size, 2_000)
        left = [str(value) for value in range(sample)]
        right = [str(value) for value in range(sample // 2, sample + sample // 2)]
        start = time.perf_counter()
        nested = nested_clashes(left, right)
        nested_time = time.perf_counter() - start
        start = time.perf_counter()
        common = set(left) & set(right)
        set_intersection_time = time.perf_counter() - start
        if nested != common:
            raise AssertionError("intersection methods disagree")
        print(
            f"{size:>9}: list membership={list_time:.6g}s, set={set_time:.6g}s; "
            f"common on {sample} values: nested={nested_time:.6g}s, set={set_intersection_time:.6g}s"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()
    ai_elective = {"192311001", "192311004", "192311007", "192311009"}
    iot_elective = {"192311002", "192311004", "192311009", "192311010"}
    all_students = {f"1923110{i:02d}" for i in range(1, 11)}
    for label, report in (
        ("operators", clash_report(ai_elective, iot_elective, all_students)),
        ("methods", clash_report_methods(ai_elective, iot_elective, all_students)),
    ):
        both, exactly_one, neither = report
        print(label, "clash:", both)
        print(label, "exactly one:", exactly_one)
        print(label, "neither:", neither)
    print("duplicates removed:", set(["R1", "R1", "R2"]))
    if args.benchmark:
        benchmark()


if __name__ == "__main__":
    main()
