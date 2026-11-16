import unittest

from Task04.electives import clash_report, clash_report_methods, nested_clashes


class ElectiveTests(unittest.TestCase):
    def test_expected_small_case(self) -> None:
        ai = {"1", "4", "7", "9"}
        iot = {"2", "4", "9", "10"}
        all_students = {str(number) for number in range(1, 11)}
        expected = (["4", "9"], ["1", "10", "2", "7"], ["3", "5", "6", "8"])
        self.assertEqual(clash_report(ai, iot, all_students), expected)
        self.assertEqual(clash_report_methods(ai, iot, all_students), expected)

    def test_empty_and_identical_electives(self) -> None:
        all_students = {"1", "2"}
        self.assertEqual(clash_report(set(), set(), all_students), ([], [], ["1", "2"]))
        self.assertEqual(
            clash_report({"1", "2"}, {"1", "2"}, all_students),
            (["1", "2"], [], []),
        )

    def test_nested_loop_result(self) -> None:
        self.assertEqual(nested_clashes(["a", "a", "b"], ["b", "c"]), {"b"})


if __name__ == "__main__":
    unittest.main()
