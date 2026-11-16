"""Bus-stop coordinate keys, independent grids, and copying experiments."""

import argparse
import copy
import sys
import time


def make_grid(rows: int, cols: int) -> list[list[int]]:
    if rows < 0 or cols < 0:
        raise ValueError("grid dimensions cannot be negative")
    return [[0 for _ in range(cols)] for _ in range(rows)]


def demonstrate_grid_aliasing(rows: int = 3, cols: int = 4) -> tuple[list[list[int]], list[list[int]]]:
    bad = [[0] * cols] * rows
    good = make_grid(rows, cols)
    if rows and cols:
        bad[0][1] = 7
        good[0][1] = 7
    return bad, good


def copy_examples() -> dict[str, object]:
    original = [["Central"], ["T Nagar"]]
    shallow = copy.copy(original)
    sliced = original[:]
    deep = copy.deepcopy(original)
    original[0].append("Beach")
    return {
        "original": original,
        "shallow": shallow,
        "slice": sliced,
        "deep": deep,
        "outer_alias": original is shallow,
        "inner_alias": original[0] is shallow[0],
        "deep_inner_alias": original[0] is deep[0],
    }


def tuple_index_demo() -> tuple[dict[tuple[float, float], str], str]:
    stops = {
        (13.0827, 80.2707): "Chennai Central",
        (13.0418, 80.2341): "T. Nagar",
    }
    return stops, stops[(13.0418, 80.2341)]


def memory_and_timing(size: int = 1_000_000) -> None:
    values = list(range(size))
    packed = tuple(values)
    print("container bytes:", sys.getsizeof(values), sys.getsizeof(packed))

    loops = 5
    for kind, factory, container in (
        ("list", list, values),
        ("tuple", tuple, packed),
    ):
        start = time.perf_counter()
        for _ in range(loops):
            factory(range(size))
        creation = (time.perf_counter() - start) / loops
        start = time.perf_counter()
        for _ in range(loops):
            _ = container[size // 2]
        indexing = (time.perf_counter() - start) / loops
        print(f"{kind}: create={creation:.6f}s, index={indexing:.8f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()
    bad, good = demonstrate_grid_aliasing()
    print("bad:", bad)
    print("good:", good)
    print("row identity:", bad[0] is bad[1], good[0] is good[1])
    stops, stop = tuple_index_demo()
    print("stop:", stop, "| coordinate keys:", list(stops))
    print("copy behavior:", copy_examples())
    grid = make_grid(3, 3)
    print("correct grid is independent:", grid[0] is not grid[1], [id(row) for row in grid])
    tuple_with_list = (["mutable child"],)
    tuple_with_list[0].append("can change")
    print("tuple/list mutability:", tuple_with_list)
    try:
        stops[[13.0418, 80.2341]] = "unhashable"
    except TypeError as error:
        print("list dictionary key:", error)
    if args.benchmark:
        memory_and_timing()


if __name__ == "__main__":
    main()
