import unittest

from Task02.tuples_copying import (
    copy_examples,
    demonstrate_grid_aliasing,
    make_grid,
    tuple_index_demo,
)


class TupleCopyingTests(unittest.TestCase):
    def test_grid_rows_are_independent(self) -> None:
        bad, good = demonstrate_grid_aliasing(3, 4)
        self.assertIs(bad[0], bad[1])
        self.assertIsNot(good[0], good[1])
        self.assertEqual(good, [[0, 7, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        self.assertEqual(make_grid(2, 3), [[0, 0, 0], [0, 0, 0]])

    def test_tuple_coordinates_are_dictionary_keys(self) -> None:
        stops, name = tuple_index_demo()
        self.assertEqual(name, "T. Nagar")
        self.assertEqual(stops[(13.0418, 80.2341)], "T. Nagar")

    def test_shallow_and_deep_copy(self) -> None:
        result = copy_examples()
        self.assertFalse(result["outer_alias"])
        self.assertTrue(result["inner_alias"])
        self.assertFalse(result["deep_inner_alias"])
        self.assertEqual(result["deep"], [["Central"], ["T Nagar"]])

    def test_invalid_grid_dimensions(self) -> None:
        with self.assertRaises(ValueError):
            make_grid(-1, 3)


if __name__ == "__main__":
    unittest.main()
