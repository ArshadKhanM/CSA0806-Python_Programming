import unittest

from Task05.sensor_readings import analyze_comprehension, analyze_loop, analyze_map_filter


class SensorReadingTests(unittest.TestCase):
    def test_all_methods_match_and_keep_original_minute_indices(self) -> None:
        values = [4, 10, 52, -55, 1]
        expected = ([4, 10, 1], [39.2, 50.0, 33.8], [1, 4])
        self.assertEqual(analyze_loop(values), expected)
        self.assertEqual(analyze_comprehension(values), expected)
        self.assertEqual(analyze_map_filter(values), expected)

    def test_all_valid_and_all_invalid_inputs(self) -> None:
        self.assertEqual(analyze_comprehension([2, 8]), ([2, 8], [35.6, 46.4], []))
        self.assertEqual(analyze_comprehension([51, -51]), ([], [], []))

    def test_empty_input(self) -> None:
        self.assertEqual(analyze_loop([]), ([], [], []))


if __name__ == "__main__":
    unittest.main()
