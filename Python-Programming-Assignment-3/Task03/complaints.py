"""Word counts and grouped reports for unstructured complaints."""

import argparse
import random
import re
import time
from collections import Counter
from collections.abc import Iterable

STOP_WORDS = {"not", "the", "a", "is", "and", "to", "of"}
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokens(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.casefold())


def frequencies(texts: Iterable[str], stop: set[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for text in texts:
        for word in tokens(text):
            if word not in stop:
                counts[word] = counts.get(word, 0) + 1
    return counts


def frequencies_setdefault(texts: Iterable[str], stop: set[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for text in texts:
        for word in tokens(text):
            if word not in stop:
                counts.setdefault(word, 0)
                counts[word] += 1
    return counts


def top(counts: dict[str, int], k: int) -> list[tuple[str, int]]:
    if k <= 0:
        return []
    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))[:k]


def group_by_district(complaints: Iterable[dict[str, str]]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for complaint in complaints:
        grouped.setdefault(complaint["district"], []).append(complaint["text"])
    return grouped


def group_by_crop(complaints: Iterable[dict[str, str]]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for complaint in complaints:
        grouped.setdefault(complaint["crop"], []).append(complaint["text"])
    return grouped


def list_count_frequencies(texts: Iterable[str], stop: set[str]) -> dict[str, int]:
    words = [word for text in texts for word in tokens(text) if word not in stop]
    return {word: words.count(word) for word in dict.fromkeys(words)}


def generate_complaints(count: int, seed: int = 3) -> list[str]:
    examples = [
        "Seeds delayed in the north district",
        "Fertiliser price is high",
        "Seeds price high and subsidy delayed",
        "Pest attack on rice crop",
        "Water supply is not available",
        "Cotton seeds quality is poor",
    ]
    rng = random.Random(seed)
    return [examples[rng.randrange(len(examples))] for _ in range(count)]


def benchmark(sizes: tuple[int, ...] = (1_000, 10_000, 100_000)) -> None:
    for size in sizes:
        texts = generate_complaints(size)
        timings: list[tuple[str, float, dict[str, int]]] = []
        for name, method in (
            ("get", frequencies),
            ("list.count", list_count_frequencies),
            ("Counter", lambda items, stop: dict(
                (word, count)
                for word, count in Counter(
                    word for text in items for word in tokens(text) if word not in stop
                ).items()
            )),
        ):
            start = time.perf_counter()
            counts = method(texts, STOP_WORDS)
            timings.append((name, time.perf_counter() - start, counts))
        if any(result != timings[0][2] for _, _, result in timings[1:]):
            raise AssertionError("frequency implementations disagree")
        print(f"{size:>7} complaints:", ", ".join(f"{n}={t:.6f}s" for n, t, _ in timings))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()
    if args.benchmark:
        benchmark()
        return
    complaints = [
        {"district": "Salem", "crop": "rice", "text": "Seeds not received seeds delayed"},
        {"district": "Salem", "crop": "rice", "text": "Fertiliser price high"},
        {"district": "Erode", "crop": "cotton", "text": "Seeds price high subsidy not received"},
    ]
    texts = [item["text"] for item in complaints]
    print("get:", frequencies(texts, {"not", "high"}))
    print("setdefault:", frequencies_setdefault(texts, {"not", "high"}))
    print("top:", top(frequencies(texts, {"not", "high"}), 3))
    print("by district:", group_by_district(complaints))
    print("by crop:", group_by_crop(complaints))


if __name__ == "__main__":
    main()
