"""Tests for adversarial data and safe SQL behavior."""

import unittest

from Task03.complete_code_sql import build_connection, station_average


class AdversarialChecksTests(unittest.TestCase):
    def test_completed_code_averages_and_injection_payload(self):
        con = build_connection()
        self.assertEqual(station_average(con, "Adyar"), 54.0)
        self.assertEqual(station_average(con, "Guindy"), 108.0)
        self.assertIsNone(station_average(con, "Adyar' OR '1'='1"))
        con.close()


if __name__ == "__main__":
    unittest.main()
