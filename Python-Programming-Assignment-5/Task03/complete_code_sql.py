"""Completed B2 executemany and parameterized query example."""

import sqlite3


READINGS = [
    ("Adyar", "2026-10-01", 48.0),
    ("Guindy", "2026-10-01", 95.0),
    ("Guindy", "2026-10-03", 121.0),
    ("Adyar", "2026-10-04", 60.0),
]


def build_connection():
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE aq (station TEXT, day TEXT, pm25 REAL)")
    con.executemany("INSERT INTO aq VALUES (?, ?, ?)", READINGS)
    con.commit()
    return con


def station_average(connection, name):
    row = connection.execute(
        "SELECT AVG(pm25) FROM aq WHERE station = ?", (name,)
    ).fetchone()
    return row[0]


if __name__ == "__main__":
    con = build_connection()
    print(station_average(con, "Adyar"), station_average(con, "Guindy"))
    print(station_average(con, "Adyar' OR '1'='1"))
    con.close()
