import unittest

from Task03.complaints import (
    frequencies,
    frequencies_setdefault,
    group_by_crop,
    group_by_district,
    list_count_frequencies,
    top,
)


class ComplaintTests(unittest.TestCase):
    def test_case_punctuation_and_stop_words(self) -> None:
        texts = ["Seeds, seeds! NOT received.", "", "received"]
        stop = {"not"}
        expected = {"seeds": 2, "received": 2}
        self.assertEqual(frequencies(texts, stop), expected)
        self.assertEqual(frequencies_setdefault(texts, stop), expected)
        self.assertEqual(list_count_frequencies(texts, stop), expected)

    def test_top_sorts_ties_alphabetically(self) -> None:
        self.assertEqual(top({"received": 2, "price": 2, "seeds": 3}, 3),
                         [("seeds", 3), ("price", 2), ("received", 2)])
        self.assertEqual(top({"a": 1}, 0), [])

    def test_grouping_by_district_and_crop(self) -> None:
        values = [
            {"district": "A", "crop": "rice", "text": "one"},
            {"district": "A", "crop": "cotton", "text": "two"},
        ]
        self.assertEqual(group_by_district(values), {"A": ["one", "two"]})
        self.assertEqual(group_by_crop(values), {"rice": ["one"], "cotton": ["two"]})


if __name__ == "__main__":
    unittest.main()
