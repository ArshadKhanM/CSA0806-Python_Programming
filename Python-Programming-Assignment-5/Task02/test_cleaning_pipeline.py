"""Tests for the cleaning and completed-code pipeline."""

import unittest
from pathlib import Path

from Task02.cleaning_pipeline import clean_text, create_database, query_examples
from Task02.complete_code_cleaning import RAW, load_clean, min_max


BASE_DIR = Path(__file__).resolve().parent


class CleaningPipelineTests(unittest.TestCase):
    def test_complete_code_skips_missing_negative_and_over_limit(self):
        rows = load_clean(RAW)
        self.assertEqual(
            rows,
            [("Adyar", "2026-10-01", 48.0),
             ("Guindy", "2026-10-01", 95.0),
             ("Guindy", "2026-10-03", 121.0)],
        )
        self.assertEqual(min_max([48.0, 95.0, 121.0]), [0.0, 0.644, 1.0])
        self.assertEqual(min_max([4.0, 4.0]), [0.0, 0.0])
        self.assertEqual(min_max([]), [])

    def test_duplicate_fault_fahrenheit_and_missing_values(self):
        rows, audit = clean_text(
            (BASE_DIR / "raw_readings.csv").read_text(encoding="utf-8"))
        self.assertEqual(audit["duplicates"], 1)
        self.assertEqual(audit["malformed_rows"], 3)
        self.assertEqual(audit["impossible"], 2)
        adyar = [row for row in rows if row["station"] == "Adyar"]
        self.assertEqual(len(adyar), 7)
        self.assertAlmostEqual(adyar[0]["temperature_c"], 25.0)
        self.assertEqual(adyar[1]["pm25"], 48.0)
        self.assertIsNone(adyar[3]["pm25"])

    def test_parameterized_database_queries(self):
        source = (BASE_DIR / "raw_readings.csv").read_text(encoding="utf-8")
        rows, _ = clean_text(source)
        con = create_database(rows)
        mean, stations, hours = query_examples(con)
        self.assertAlmostEqual(mean, 51.8)
        self.assertEqual([station for station, _ in stations],
                         ["Adyar", "Guindy", "Marina"])
        self.assertTrue(hours)
        con.close()

    def test_missing_column_fails_clearly(self):
        with self.assertRaisesRegex(ValueError, "missing required columns"):
            clean_text("station,date,pm25\nAdyar,2026-10-01,10\n")


if __name__ == "__main__":
    unittest.main()
