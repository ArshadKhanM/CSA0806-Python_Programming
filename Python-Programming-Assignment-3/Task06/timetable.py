"""Train timetable queries with and without a station-to-trains index."""

import argparse
import sys
import time
from collections.abc import Mapping

Stop = tuple[str, str, str]  # station, arrival, departure
Train = dict[str, object]
Timetable = dict[str, Train]


def demo_timetable() -> Timetable:
    return {
        "12601": {
            "name": "Chennai Mail",
            "stops": [
                ("Chennai Central", "06:00", "06:10"),
                ("Arakkonam", "07:20", "07:25"),
                ("Katpadi", "08:40", "08:45"),
            ],
            "days": {"Mon", "Wed", "Fri"},
        },
        "12602": {
            "name": "Coastal Express",
            "stops": [
                ("Chennai Central", "07:00", "07:15"),
                ("Tambaram", "07:35", "07:40"),
                ("Chengalpattu", "08:15", "08:20"),
            ],
            "days": {"Tue", "Thu", "Sat"},
        },
        "12603": {
            "name": "Hill Passenger",
            "stops": [
                ("Beach", "05:50", "05:55"),
                ("Chennai Central", "06:05", "06:15"),
                ("Arakkonam", "08:00", "08:05"),
            ],
            "days": {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat"},
        },
        "12604": {
            "name": "Southern Link",
            "stops": [
                ("Chennai Central", "09:00", "09:10"),
                ("Katpadi", "11:00", "11:05"),
                ("Jolarpettai", "12:10", "12:15"),
            ],
            "days": {"Sun"},
        },
        "12605": {
            "name": "City Intercity",
            "stops": [
                ("Tambaram", "08:00", "08:05"),
                ("Chengalpattu", "08:40", "08:45"),
                ("Villupuram", "10:00", "10:05"),
            ],
            "days": {"Mon", "Tue", "Wed", "Thu", "Fri"},
        },
    }


def build_station_index(timetable: Mapping[str, Train]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for train_number, train in timetable.items():
        for station, _, _ in train["stops"]:  # type: ignore[union-attr]
            index.setdefault(station, []).append(train_number)
    return index


def _departure(train: Train, station: str) -> str | None:
    for stop, _, departure in train["stops"]:  # type: ignore[union-attr]
        if stop == station:
            return departure
    return None


def query_without_index(
    timetable: Mapping[str, Train], station: str, day: str
) -> list[tuple[str, str, str]]:
    result = []
    for train_number, train in timetable.items():
        if day not in train["days"]:  # type: ignore[operator]
            continue
        departure = _departure(train, station)
        if departure is not None:
            result.append((train_number, train["name"], departure))  # type: ignore[arg-type]
    return sorted(result, key=lambda row: row[2])


def query_with_index(
    timetable: Mapping[str, Train],
    index: Mapping[str, list[str]],
    station: str,
    day: str,
) -> list[tuple[str, str, str]]:
    result = []
    for train_number in index.get(station, []):
        train = timetable[train_number]
        if day not in train["days"]:  # type: ignore[operator]
            continue
        departure = _departure(train, station)
        if departure is not None:
            result.append((train_number, train["name"], departure))  # type: ignore[arg-type]
    return sorted(result, key=lambda row: row[2])


def generate_timetable(train_count: int) -> Timetable:
    stations = [f"Station-{index:02d}" for index in range(50)]
    days = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    timetable: Timetable = {}
    for train_id in range(train_count):
        first = train_id % len(stations)
        stops: list[Stop] = []
        for offset in range(8):
            minutes = (train_id * 7 + offset * 37) % (24 * 60)
            hour, minute = divmod(minutes, 60)
            arrival = f"{hour:02d}:{minute:02d}"
            departure_hour, departure_minute = divmod((minutes + 3) % (24 * 60), 60)
            departure = f"{departure_hour:02d}:{departure_minute:02d}"
            stops.append((stations[(first + offset * 3) % len(stations)], arrival, departure))
        timetable[f"T{train_id:05d}"] = {
            "name": f"Generated Train {train_id}",
            "stops": stops,
            "days": {days[train_id % 7], days[(train_id + 2) % 7]},
        }
    return timetable


def benchmark(sizes: tuple[int, ...] = (100, 1_000, 10_000)) -> None:
    for count in sizes:
        timetable = generate_timetable(count)
        index = build_station_index(timetable)
        station = "Station-10"
        queries = 100
        start = time.perf_counter()
        for _ in range(queries):
            plain = query_without_index(timetable, station, "Mon")
        plain_time = (time.perf_counter() - start) / queries
        start = time.perf_counter()
        for _ in range(queries):
            indexed = query_with_index(timetable, index, station, "Mon")
        indexed_time = (time.perf_counter() - start) / queries
        if plain != indexed:
            raise AssertionError("indexed and scan queries disagree")
        shallow_bytes = sys.getsizeof(index) + sum(sys.getsizeof(ids) for ids in index.values())
        print(
            f"{count:>6} trains: scan={plain_time:.6f}s/query, "
            f"indexed={indexed_time:.6f}s/query, index containers={shallow_bytes} bytes"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()
    timetable = demo_timetable()
    station_index = build_station_index(timetable)
    station, day = "Chennai Central", "Mon"
    print("nested structure example:", timetable["12601"])
    print("third stop departure:", timetable["12601"]["stops"][2][2])  # type: ignore[index]
    print("query scan:", query_without_index(timetable, station, day))
    print("query index:", query_with_index(timetable, station_index, station, day))
    print("unknown station:", query_with_index(timetable, station_index, "Atlantis", day))
    print("station index keys:", sorted(station_index))
    if args.benchmark:
        benchmark()


if __name__ == "__main__":
    main()
