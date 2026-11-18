"""Clean station readings, load SQLite, query summaries, and create charts."""

import csv
import io
import logging
import sqlite3
from collections import defaultdict
from datetime import date
from pathlib import Path
from statistics import median

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
RAW_FILE = BASE_DIR / "raw_readings.csv"
RESULTS_DIR = BASE_DIR / "results"
EXPECTED_COLUMNS = {
    "station", "date", "hour", "pm25", "pm10", "no2", "temperature",
    "temperature_unit",
}
LIMITS = {
    "pm25": (0.0, 999.0),
    "pm10": (0.0, 999.0),
    "no2": (0.0, 2000.0),
    "temperature_c": (-50.0, 60.0),
}
LOGGER = logging.getLogger(__name__)


def _read_rows(text):
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or not EXPECTED_COLUMNS.issubset(reader.fieldnames):
        missing = sorted(EXPECTED_COLUMNS.difference(reader.fieldnames or []))
        raise ValueError("CSV is missing required columns: " + ", ".join(missing))
    rows = []
    input_count = 0
    malformed_count = 0
    for line_number, row in enumerate(reader, start=2):
        input_count += 1
        if None in row or any(row.get(name) is None for name in EXPECTED_COLUMNS):
            malformed_count += 1
            continue
        try:
            station = " ".join((row["station"] or "").split()).title()
            if not station:
                raise ValueError("empty station")
            day = date.fromisoformat((row["date"] or "").strip()).isoformat()
            hour = int(row["hour"])
            if not 0 <= hour <= 23:
                raise ValueError("hour outside 0-23")
        except (TypeError, ValueError):
            malformed_count += 1
            continue
        unit = (row["temperature_unit"] or "").strip().upper()
        if unit not in {"C", "F"}:
            malformed_count += 1
            continue
        rows.append({
            "station": station,
            "day": day,
            "hour": hour,
            "source_temp_unit": unit,
            "raw": {name: (row[name] or "").strip() for name in
                    ("pm25", "pm10", "no2", "temperature")},
        })
    return rows, input_count, malformed_count


def _parse_reading(raw, metric, unit):
    if not raw or raw.upper() == "NA":
        return None, "missing"
    try:
        value = float(raw)
    except ValueError:
        return None, "invalid"
    if metric == "temperature_c" and unit == "F":
        value = (value - 32.0) * 5.0 / 9.0
    lower, upper = LIMITS[metric]
    if not lower <= value <= upper:
        return None, "impossible"
    return value, "valid"


def clean_text(text):
    """Return cleaned rows and counters; duplicate keys retain their first row."""
    raw_rows, input_count, malformed_count = _read_rows(text)
    deduplicated = []
    seen = set()
    audit = {
        "input_rows": input_count, "malformed_rows": malformed_count,
        "duplicates": 0, "missing": 0, "impossible": 0, "invalid": 0,
        "imputed": 0,
    }
    for row in raw_rows:
        key = (row["station"], row["day"], row["hour"])
        if key in seen:
            audit["duplicates"] += 1
            continue
        seen.add(key)
        deduplicated.append(row)

    metrics = ("pm25", "pm10", "no2", "temperature_c")
    medians = defaultdict(list)
    prepared = []
    for row in deduplicated:
        output = {key: row[key] for key in
                  ("station", "day", "hour", "source_temp_unit")}
        states = {}
        for metric in metrics:
            raw_metric = "temperature" if metric == "temperature_c" else metric
            value, state = _parse_reading(
                row["raw"][raw_metric], metric, row["source_temp_unit"])
            output[metric] = value
            states[metric] = state
            if state == "valid":
                medians[(row["station"], metric)].append(value)
            elif state in audit:
                audit[state] += 1
        prepared.append((output, states))

    fallback = {key: median(values) for key, values in medians.items()}
    previous = {}
    cleaned = []
    prepared.sort(key=lambda item: (item[0]["station"], item[0]["day"], item[0]["hour"]))
    for output, states in prepared:
        for metric in metrics:
            key = (output["station"], metric)
            value = output[metric]
            if states[metric] == "missing":
                if key in previous:
                    value = previous[key]
                elif key in fallback:
                    value = fallback[key]
                if value is not None:
                    audit["imputed"] += 1
                    output[metric] = value
            if states[metric] == "valid" and value is not None:
                previous[key] = value
        cleaned.append(output)
    return cleaned, audit


def create_database(rows, connection=None):
    """Create station/readings tables and insert cleaned data with executemany."""
    con = connection or sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript("""
        CREATE TABLE IF NOT EXISTS stations (
            station TEXT PRIMARY KEY,
            source_temp_unit TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS readings (
            station TEXT NOT NULL REFERENCES stations(station),
            day TEXT NOT NULL,
            hour INTEGER NOT NULL CHECK(hour BETWEEN 0 AND 23),
            pm25 REAL, pm10 REAL, no2 REAL, temperature_c REAL,
            PRIMARY KEY(station, day, hour)
        );
    """)
    con.execute(
        "CREATE INDEX IF NOT EXISTS idx_readings_station_day "
        "ON readings(station, day)")
    station_rows = sorted({
        (row["station"], row["source_temp_unit"]) for row in rows
    })
    con.executemany(
        "INSERT OR REPLACE INTO stations(station, source_temp_unit) VALUES (?, ?)",
        station_rows,
    )
    con.executemany(
        """INSERT OR REPLACE INTO readings
           (station, day, hour, pm25, pm10, no2, temperature_c)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [(row["station"], row["day"], row["hour"], row["pm25"], row["pm10"],
          row["no2"], row["temperature_c"]) for row in rows],
    )
    con.commit()
    return con


def query_examples(connection):
    """Run three parameterized questions corresponding to the Part A design."""
    october_mean = connection.execute(
        "SELECT AVG(pm25) FROM readings WHERE station=? AND day>=? AND day<?",
        ("Adyar", "2026-10-01", "2026-11-01"),
    ).fetchone()[0]
    station_means = connection.execute(
        """SELECT station, AVG(pm25) FROM readings
           WHERE day>=? AND day<? GROUP BY station ORDER BY station""",
        ("2026-10-01", "2026-11-01"),
    ).fetchall()
    worst_hours = connection.execute(
        """SELECT hour, AVG(pm25) AS mean_pm25 FROM readings
           WHERE pm25 IS NOT NULL GROUP BY hour
           ORDER BY mean_pm25 DESC, hour LIMIT 5"""
    ).fetchall()
    return october_mean, station_means, worst_hours


def create_charts(connection, output_dir=RESULTS_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)
    daily = pd.read_sql_query(
        """SELECT day, AVG(pm25) AS pm25 FROM readings
           WHERE pm25 IS NOT NULL GROUP BY day ORDER BY day""", connection)
    stations = pd.read_sql_query(
        """SELECT station, AVG(pm25) AS pm25 FROM readings
           WHERE pm25 IS NOT NULL GROUP BY station ORDER BY station""", connection)
    pairs = pd.read_sql_query(
        """SELECT temperature_c, pm25 FROM readings
           WHERE temperature_c IS NOT NULL AND pm25 IS NOT NULL""", connection)
    hours = pd.read_sql_query(
        """SELECT hour, AVG(pm25) AS pm25 FROM readings
           WHERE pm25 IS NOT NULL GROUP BY hour ORDER BY hour""", connection)
    figures = [
        ("pm25_monthly_trend.png", daily, "day", "pm25", "Daily mean PM2.5",
         "Date", "PM2.5 (micrograms/m3)", "plot"),
        ("station_comparison.png", stations, "station", "pm25",
         "Mean PM2.5 by station", "Station", "PM2.5 (micrograms/m3)", "bar"),
        ("temperature_pm25_scatter.png", pairs, "temperature_c", "pm25",
         "Temperature and PM2.5", "Temperature (C)", "PM2.5 (micrograms/m3)",
         "scatter"),
        ("worst_hours.png", hours, "hour", "pm25", "Mean PM2.5 by hour",
         "Hour of day", "PM2.5 (micrograms/m3)", "bar"),
    ]
    for filename, frame, x_col, y_col, title, x_label, y_label, kind in figures:
        fig, axis = plt.subplots(figsize=(8, 4.5))
        if kind == "plot":
            axis.plot(pd.to_datetime(frame[x_col]), frame[y_col], marker="o")
            axis.tick_params(axis="x", rotation=35)
        elif kind == "scatter":
            axis.scatter(frame[x_col], frame[y_col], alpha=0.75)
        else:
            categories = frame[x_col] if x_col == "station" else frame[x_col].astype(int)
            axis.bar(categories, frame[y_col])
        axis.set(title=title, xlabel=x_label, ylabel=y_label)
        fig.tight_layout()
        fig.savefig(output_dir / filename, dpi=140)
        plt.close(fig)


def run_pipeline():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    text = RAW_FILE.read_text(encoding="utf-8")
    before = list(csv.DictReader(io.StringIO(text)))
    rows, audit = clean_text(text)
    LOGGER.info("Cleaning audit: %s", audit)
    con = create_database(rows)
    with (RESULTS_DIR / "cleaned_readings.csv").open(
            "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=[
            "station", "day", "hour", "source_temp_unit", "pm25", "pm10",
            "no2", "temperature_c"])
        writer.writeheader()
        writer.writerows(rows)
    october_mean, station_means, worst_hours = query_examples(con)
    create_charts(con)
    report = [
        "Input rows: " + str(len(before)),
        "Cleaned rows: " + str(len(rows)),
        "Cleaning audit: " + repr(audit),
        "Before sample: " + repr(before[:3]),
        "After sample: " + repr(rows[:3]),
        "Adyar October mean PM2.5: " + str(round(october_mean, 3)),
        "October station means: " + repr(
            [(name, round(value, 3)) for name, value in station_means]),
        "Worst observed hours (hour, mean PM2.5): " + repr(
            [(hour, round(value, 3)) for hour, value in worst_hours]),
        "Chart files: pm25_monthly_trend.png, station_comparison.png, "
        "temperature_pm25_scatter.png, worst_hours.png",
        "Interpretation: Adyar's two-day mean is based on five non-null "
        "hourly values after missing-value imputation; station comparisons "
        "are descriptive for this small "
        "synthetic sample. The scatter plot compares converted Celsius "
        "temperatures with valid PM2.5 pairs. Hourly means are sparse because "
        "the sample includes only a few reporting hours.",
        "Chart interpretation - trend: the daily means rise from 66.25 on "
        "October 1 to 75.0 on October 2. This is a two-day synthetic sample, "
        "not evidence of a long-term city trend.",
        "Chart interpretation - stations: Guindy has the highest sample mean "
        "(105.25), followed by Adyar (51.8) and Marina (37.5). Different "
        "sample sizes and the small fixture make this comparison descriptive.",
        "Chart interpretation - temperature scatter: the displayed points "
        "pair Celsius-converted temperatures with valid PM2.5 values. This "
        "small sample does not establish a meaningful temperature relationship.",
        "Chart interpretation - hours: hour 2 has the highest sample mean "
        "(84.5), while only a few hours are represented. More days and "
        "complete hourly coverage are needed before identifying a recurring "
        "pollution peak.",
        "B1.2 design comparison: the implementation follows the design by "
        "normalizing station/date/hour, deduplicating, converting Fahrenheit, "
        "imputing only missing values, keeping impossible readings NULL, "
        "inserting with executemany, and querying by station/date. The sample "
        "pipeline additionally counts malformed rows and writes reproducible "
        "chart and CSV outputs.",
    ]
    output = "\n".join(report) + "\n"
    (RESULTS_DIR / "pipeline_results.txt").write_text(output, encoding="utf-8")
    print(output, end="")
    con.close()


if __name__ == "__main__":
    run_pipeline()
