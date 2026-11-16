import unittest

from Task07.contacts import (
    merge_contacts,
    merge_contacts_pairwise,
    normalize_name,
    normalize_phone,
)


class ContactTests(unittest.TestCase):
    def test_phone_and_name_normalization(self) -> None:
        self.assertEqual(normalize_phone("+91 98400 12345"), "9840012345")
        self.assertEqual(normalize_name("Dr. Ravi"), "dr ravi")

    def test_duplicate_formats_emails_and_transitive_merges(self) -> None:
        contacts = [
            {"name": "Dr. Ravi", "phones": ["+91 98400 12345"], "emails": ["R@EXAMPLE.COM"]},
            {"name": "ravi kumar", "phones": ["9840012345"], "emails": ["r@example.com"]},
            {"name": "Mina", "phones": ["9000011111"], "emails": []},
            {"name": "Ravi", "phones": ["9840012345", "9000011111"], "emails": ["other@example.com"]},
        ]
        result = merge_contacts(contacts)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["numbers"], ["9000011111", "9840012345"])
        self.assertEqual(result[0]["emails"], ["other@example.com", "r@example.com"])
        self.assertEqual(result[0]["name"], "Dr. Ravi")

    def test_same_name_without_shared_number_stays_separate(self) -> None:
        contacts = [
            {"name": "Ravi", "phones": ["9840012345"]},
            {"name": "Ravi", "phones": ["9840011111"]},
        ]
        self.assertEqual(len(merge_contacts(contacts)), 2)

    def test_missing_fields_and_pairwise_agreement(self) -> None:
        contacts = [
            {"name": "No number"},
            {"name": "No number"},
            {"name": "Has number", "phone": "9000012345", "email": "A@EXAMPLE.COM"},
        ]
        self.assertEqual(merge_contacts(contacts), merge_contacts_pairwise(contacts))
        self.assertEqual(len(merge_contacts(contacts)), 3)


if __name__ == "__main__":
    unittest.main()
