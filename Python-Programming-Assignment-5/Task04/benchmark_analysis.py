"""Compare CSV-loop, pandas, and SQLite aggregation at three data sizes."""

import cProfile
import csv
import io
import math
import pstats
import sqlite3
import tempfile
import time
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


RESULTS_DIR = Path(__file__).resolve().parent / "results"
STATIONS = (1, 12, 120)
HOURS_PER_DAY = 24
DAYS_PER_YEAR = 365
BATCH_SIZE = 10000


def generate_csv(path, station_count):
    """Create one deterministic year of hourly data per station."""
    start = date(2026, 1, 1)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("station", "day", "hour", "pm25"))
        for station_index in range(station_count):
            station = f"Station{station_index + 1:03d}"
            for day_index in range(DAYS_PER_YEAR):
                day = (start + timedelta(days=day_index)).isoformat()
                for hour in range(HOURS_PER_DAY):
                    pm25 = float(10 + (station_index % 40) + day_index % 30 + hour % 12)
                    writer.writerow((station, day, hour, pm25))


def loop_group(path):
    """Stream CSV and retain running sums/counts per station and day."""
    totals = defaultdict(lambda: [0.0, 0])
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            key = (row["station"], row["day"])
            totals[key][0] += float(row["pm25"])
            totals[key][1] += 1
    return {key: pair[0] / pair[1] for key, pair in totals.items()}


def generate_dirty_pm25_csv(path, row_count):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("station", "date", "pm25"))
        for index in range(row_count):
            if index % 103 == 0:
                value = ""
            elif index % 107 == 0:
                value = "NA"
            elif index % 109 == 0:
                value = -5
            elif index % 113 == 0:
                value = 1200
            else:
                value = 10 + index % 300
            writer.writerow(("Adyar", "2026-10-01", value))


def csv_clean_minmax(path):
    values = []
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            raw_value = (row["pm25"] or "").strip()
            if not raw_value or raw_value.upper() == "NA":
                continue
            value = float(raw_value)
            if 0 <= value <= 999:
                values.append(value)
    if not values:
        return values, []
    minimum, maximum = min(values), max(values)
    if minimum == maximum:
        return values, [0.0 for _ in values]
    return values, [round((value - minimum) / (maximum - minimum), 3)
                    for value in values]


def pandas_clean_minmax(path):
    frame = pd.read_csv(path)
    values = pd.to_numeric(frame["pm25"], errors="coerce")
    values = values[values.between(0, 999)].astype(float)
    if values.empty:
        normalized = []
    elif values.min() == values.max():
        normalized = [0.0 for _ in values]
    else:
        normalized = ((values - values.min()) /
                      (values.max() - values.min())).round(3).tolist()
    return values.tolist(), [float(value) for value in normalized], int(
        frame.memory_usage(index=True, deep=True).sum())


def pandas_group(path):
    frame = pd.read_csv(path)
    grouped = frame.groupby(["station", "day"], sort=True)["pm25"].mean()
    return {key: float(value) for key, value in grouped.items()}, int(
        frame.memory_usage(index=True, deep=True).sum())


def _insert_csv(connection, path):
    batch = []
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            batch.append((row["station"], row["day"], int(row["hour"]),
                          float(row["pm25"])))
            if len(batch) == BATCH_SIZE:
                connection.executemany(
                    "INSERT INTO readings VALUES (?, ?, ?, ?)", batch)
                batch.clear()
        if batch:
            connection.executemany("INSERT INTO readings VALUES (?, ?, ?, ?)", batch)


def sql_group(path, indexed=False):
    con = sqlite3.connect(":memory:")
    con.execute(
        """CREATE TABLE readings (
           station TEXT, day TEXT, hour INTEGER, pm25 REAL,
           PRIMARY KEY(station, day, hour))"""
    )
    _insert_csv(con, path)
    if indexed:
        con.execute("CREATE INDEX idx_station_day ON readings(station, day)")
    result = {
        (station, day): value
        for station, day, value in con.execute(
            """SELECT station, day, AVG(pm25) FROM readings
               GROUP BY station, day ORDER BY station, day""")
    }
    con.close()
    return result


def assert_same(expected, actual):
    if expected.keys() != actual.keys():
        raise AssertionError("Aggregation methods returned different groups")
    for key in expected:
        if not math.isclose(expected[key], actual[key], rel_tol=1e-12, abs_tol=1e-12):
            raise AssertionError("Aggregation mismatch for " + repr(key))


def elapsed(function, *args):
    start = time.perf_counter()
    result = function(*args)
    return result, time.perf_counter() - start


def profile_loop(path):
    profiler = cProfile.Profile()
    profiler.enable()
    loop_group(path)
    profiler.disable()
    buffer = io.StringIO()
    pstats.Stats(profiler, stream=buffer).strip_dirs().sort_stats(
        "cumulative").print_stats(8)
    return buffer.getvalue()


def benchmark_cleaning_sizes(root):
    lines = [
        "CSV module vs pandas cleaning/min-max at the requested input sizes:",
        "Rows | CSV seconds | pandas seconds | pandas frame bytes | valid values",
    ]
    for row_count in (1000, 100000, 1000000):
        path = root / f"dirty_pm25_{row_count}.csv"
        generate_dirty_pm25_csv(path, row_count)
        (csv_values, csv_scaled), csv_seconds = elapsed(csv_clean_minmax, path)
        (pandas_values, pandas_scaled, memory_bytes), pandas_seconds = elapsed(
            pandas_clean_minmax, path)
        if csv_values != pandas_values or csv_scaled != pandas_scaled:
            raise AssertionError("CSV and pandas cleaning results differ")
        lines.append(
            f"{row_count:7d} | {csv_seconds:.4f} | {pandas_seconds:.4f} "
            f"| {memory_bytes} | {len(csv_values)}"
        )
    return lines


def index_timings(path, station="Station001", day="2026-10-01", repeats=5):
    con = sqlite3.connect(":memory:")
    con.execute(
        """CREATE TABLE readings (
           station TEXT, day TEXT, hour INTEGER, pm25 REAL)"""
    )
    _insert_csv(con, path)
    query = "SELECT AVG(pm25) FROM readings WHERE station=? AND day=?"

    def run_queries():
        for _ in range(repeats):
            con.execute(query, (station, day)).fetchone()

    start = time.perf_counter()
    run_queries()
    scan_time = time.perf_counter() - start
    plan_before = con.execute("EXPLAIN QUERY PLAN " + query, (station, day)).fetchall()
    con.execute("CREATE INDEX idx_station_day ON readings(station, day)")
    start = time.perf_counter()
    run_queries()
    indexed_time = time.perf_counter() - start
    plan_after = con.execute("EXPLAIN QUERY PLAN " + query, (station, day)).fetchall()
    con.close()
    return scan_time, indexed_time, plan_before, plan_after


def run_benchmarks():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report = [
        "Input: deterministic hourly PM2.5 values; generation excluded from timings.",
        "Each method includes reading/parsing the CSV; SQL includes batched "
        "database load and GROUP BY. One run per size; timings vary by machine.",
        "",
        "Stations | Readings | Loop seconds | pandas seconds | SQL seconds | "
        "pandas frame bytes | groups",
    ]
    with tempfile.TemporaryDirectory(prefix="aq_assignment5_") as temporary:
        root = Path(temporary)
        report.extend(["", *benchmark_cleaning_sizes(root), ""])
        largest_path = None
        profile_path = None
        for station_count in STATIONS:
            path = root / f"readings_{station_count}.csv"
            generate_csv(path, station_count)
            if station_count == 120:
                largest_path = path
            if station_count == 12:
                profile_path = path
            loop_result, loop_seconds = elapsed(loop_group, path)
            pandas_result, pandas_seconds = elapsed(pandas_group, path)
            sql_result, sql_seconds = elapsed(sql_group, path)
            pandas_values, memory_bytes = pandas_result
            assert_same(loop_result, pandas_values)
            assert_same(loop_result, sql_result)
            report.append(
                f"{station_count:8d} | {station_count * DAYS_PER_YEAR * HOURS_PER_DAY:8d} "
                f"| {loop_seconds:.4f} | {pandas_seconds:.4f} | {sql_seconds:.4f} "
                f"| {memory_bytes} | {len(loop_result)}"
            )

        report.extend(["", "cProfile: plain Python loop on 12 stations (105,120 rows):",
                       profile_loop(profile_path)])
        scan, indexed, plan_before, plan_after = index_timings(largest_path)
        report.extend([
            "Composite-index experiment on 1,051,200 readings (five repeated "
            "station/day averages):",
            f"Without index: {scan:.6f} seconds",
            f"With (station, day) index: {indexed:.6f} seconds",
            "Query plan before: " + repr(plan_before),
            "Query plan after: " + repr(plan_after),
            "",
            "Interpretation: all three methods matched every station/day mean. "
            "The loop is transparent and streams input while retaining only "
            "group totals; pandas is concise and vectorized but materializes "
            "the DataFrame; SQLite adds ingestion cost before reusable SQL "
            "queries. Use pandas for a quick one-off exploration and SQLite "
            "for repeatable automated reports. cProfile attributes most work "
            "to CSV iteration/conversion and dictionary aggregation. An index "
            "benefits selective station/day lookups, not an all-row GROUP BY.",
            "",
            "Production decision: at 112 stations reporting every 15 minutes, "
            "the network would generate 3,924,480 readings/year before "
            "retention. Use validated batch ingestion into a managed relational "
            "database (PostgreSQL with date partitioning, station/date indexes, "
            "and daily aggregate tables), retain immutable source files, and "
            "monitor rejected/imputed readings. Keep human-reviewed lexicon "
            "triage initially for 50,000 complaints/month (600,000/year); "
            "evaluate a "
            "privacy-reviewed, multilingual classifier against labeled local "
            "complaints before replacing it. "
            "The measured lexicon results and workload are not enough evidence "
            "to deploy a large language model without a validation study.",
        ])
    output = "\n".join(report) + "\n"
    (RESULTS_DIR / "benchmark_results.txt").write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    run_benchmarks()
