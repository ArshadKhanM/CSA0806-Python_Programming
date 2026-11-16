import unittest

from Task06.timetable import (
    build_station_index,
    demo_timetable,
    generate_timetable,
    query_with_index,
    query_without_index,
)


class TimetableTests(unittest.TestCase):
    def test_indexed_and_scan_queries_match_and_sort(self) -> None:
        trains = demo_timetable()
        index = build_station_index(trains)
        expected = query_without_index(trains, "Chennai Central", "Mon")
        self.assertEqual(query_with_index(trains, index, "Chennai Central", "Mon"), expected)
        self.assertEqual([row[2] for row in expected], sorted(row[2] for row in expected))

    def test_unknown_station_and_non_running_day(self) -> None:
        trains = demo_timetable()
        index = build_station_index(trains)
        self.assertEqual(query_with_index(trains, index, "Unknown", "Mon"), [])
        self.assertEqual(query_with_index(trains, index, "Chennai Central", "Sun"), [
            ("12604", "Southern Link", "09:10")
        ])
        self.assertEqual(query_with_index(trains, index, "Beach", "Sun"), [])

    def test_synthetic_timetable_query(self) -> None:
        trains = generate_timetable(100)
        index = build_station_index(trains)
        self.assertEqual(
            query_with_index(trains, index, "Station-10", "Mon"),
            query_without_index(trains, "Station-10", "Mon"),
        )


if __name__ == "__main__":
    unittest.main()
