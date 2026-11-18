"""Tests for sentiment, extractive summary, and question answering."""

import unittest
from collections import Counter

from Task02.cleaning_pipeline import clean_text, create_database
from Task05.complaint_ai import (
    answer_question, label, read_complaints, score, summarize,
)


class ComplaintAiTests(unittest.TestCase):
    def test_sentiment_and_negation(self):
        self.assertEqual(label("Roads are clean and the bus was fast."), "positive")
        self.assertEqual(label("Smoke from the factory, air is bad."), "negative")
        self.assertEqual(label("The staff were not helpful."), "negative")
        self.assertEqual(label("Not bad, service improved."), "positive")
        self.assertEqual(score("not never good"), -1)

    def test_summary_selects_important_sentence(self):
        text = "This complaint was recorded today. Factory smoke is bad."
        frequencies = Counter({"factory": 4, "smoke": 10, "bad": 8})
        self.assertEqual(summarize(text, frequencies), "Factory smoke is bad.")

    def test_dataset_has_at_least_fifty_and_expected_labels(self):
        complaints = read_complaints()
        self.assertGreaterEqual(len(complaints), 50)
        self.assertEqual(len({row["id"] for row in complaints}), len(complaints))

    def test_chatbot_parameterizes_station_and_date(self):
        from pathlib import Path
        source = (Path(__file__).resolve().parent.parent / "Task02"
                  / "raw_readings.csv").read_text(encoding="utf-8")
        rows, _ = clean_text(source)
        con = create_database(rows)
        answer = answer_question(
            "What is the PM2.5 in Adyar today?", con, today="2026-10-01")
        self.assertIn("48.0", answer)
        self.assertEqual(answer_question(
            "What is PM2.5 in Adyar' OR '1'='1 today?", con,
            today="2026-10-01"), answer)
        con.close()


if __name__ == "__main__":
    unittest.main()
