"""Demonstrate malformed source handling and parameterized SQL safety."""

import csv
import io
import sqlite3
from pathlib import Path

from Task02.cleaning_pipeline import clean_text
from Task03.complete_code_sql import READINGS, build_connection, station_average


RESULTS_DIR = Path(__file__).resolve().parent / "results"


def inspect_source(name, content):
    try:
        clean_text(content)
    except (ValueError, csv.Error) as error:
        return name + ": rejected: " + str(error)
    return name + ": accepted"


def demonstrate_sql_injection():
    con = build_connection()
    payload = "Adyar' OR '1'='1"
    unsafe_sql = "SELECT station, day, pm25 FROM aq WHERE station = '" + payload + "'"
    unsafe_rows = con.execute(unsafe_sql).fetchall()
    safe_rows = con.execute(
        "SELECT station, day, pm25 FROM aq WHERE station = ?", (payload,)
    ).fetchall()
    result = (
        "Injection payload: " + repr(payload) + "\n"
        + "String-built query returned " + str(len(unsafe_rows)) + " rows\n"
        + "Parameterized query returned " + str(len(safe_rows)) + " rows\n"
        + "Complete-code station averages: "
        + repr((station_average(con, "Adyar"), station_average(con, "Guindy"),
                station_average(con, payload)))
    )
    con.close()
    return result


def sentiment_edge_cases():
    examples = [
        "The air is good, but the road is dirty.",
        "Not bad, but not good either.",
        "Not never good.",
        "Great, another clean-air day (sarcasm).",
    ]
    positive = {"good", "clean", "fast", "helpful", "improved"}
    negative = {"bad", "dirty", "slow", "rude", "smoke", "broken"}
    negators = {"not", "never", "no"}
    output = []
    for text in examples:
        words = [token.strip(".,!?;:()") for token in text.lower().split()]
        total = 0
        for index, word in enumerate(words):
            value = 1 if word in positive else -1 if word in negative else 0
            if index > 0 and words[index - 1] in negators:
                value *= -1
            total += value
        label = "positive" if total > 0 else "negative" if total < 0 else "neutral"
        output.append(f"{label:8} score={total:+d} | {text}")
    return output


def run_checks():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    valid_header = (
        "station,date,hour,pm25,pm10,no2,temperature,temperature_unit\n"
    )
    missing_column = "station,date,pm25\nAdyar,2026-10-01,10\n"
    wrong_delimiter = valid_header.replace(",", ";") + (
        "Adyar;2026-10-01;0;10;20;3;25;C\n"
    )
    latin1 = (valid_header + "Café,2026-10-01,0,10,20,3,25,C\n").encode("latin-1")
    try:
        latin1.decode("utf-8")
        encoding_result = "Latin-1 bytes: accepted as UTF-8"
    except UnicodeDecodeError as error:
        encoding_result = "Latin-1 bytes: rejected by UTF-8 decoder: " + str(error)
    malformed = [
        inspect_source("missing column", missing_column),
        inspect_source("wrong delimiter", wrong_delimiter),
        encoding_result,
    ]
    try:
        clean_text("")
        malformed.append("empty file: accepted")
    except ValueError as error:
        malformed.append("empty file: rejected: " + str(error))

    injection = demonstrate_sql_injection()
    lines = [
        "Malformed-source responses:",
        *malformed,
        "",
        injection,
        "",
        "Lexicon scorer adversarial examples (sarcasm and compositional limits):",
        *sentiment_edge_cases(),
        "",
        "Interpretation: required-column validation catches incomplete and "
        "semicolon-delimited files; UTF-8 decoding rejects incompatible bytes; "
        "an empty source is not a valid dataset. Interpolated SQL treats the "
        "payload as syntax and returns every row, while a ? placeholder treats "
        "it as a literal station name and returns no rows. The simple sentiment "
        "rule can cancel mixed opinions but cannot detect sarcasm or compose "
        "multiple negators correctly. Both executemany and n execute calls "
        "perform O(n) inserts; executemany reduces per-row Python call overhead "
        "and one transaction avoids committing each record separately.",
    ]
    output = "\n".join(lines) + "\n"
    (RESULTS_DIR / "adversarial_results.txt").write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    run_checks()
