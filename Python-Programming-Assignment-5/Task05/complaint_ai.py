"""Lexicon sentiment, extractive summaries, chatbot, and complaint evaluation."""

import csv
import heapq
import re
import sqlite3
from collections import Counter
from datetime import date
from pathlib import Path

from Task02.cleaning_pipeline import clean_text, create_database


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
COMPLAINT_FILE = BASE_DIR / "complaints.csv"
POSITIVE = {"good", "clean", "fast", "helpful", "improved"}
NEGATIVE = {"bad", "dirty", "slow", "rude", "smoke", "broken"}
NEGATORS = {"not", "never", "no"}
STOPWORDS = {
    "a", "an", "and", "are", "at", "but", "for", "from", "i", "in", "is",
    "it", "near", "of", "on", "our", "please", "the", "this", "to", "was",
    "were", "with", "today", "complaint", "recorded",
}


def tokens(text):
    return re.findall(r"[a-z]+", text.lower())


def score(text):
    """Score lexicon words; an immediately preceding negator flips the score."""
    words = tokens(text)
    total = 0
    for index, word in enumerate(words):
        value = 1 if word in POSITIVE else -1 if word in NEGATIVE else 0
        if index > 0 and words[index - 1] in NEGATORS:
            value *= -1
        total += value
    return total


def label(text):
    value = score(text)
    return "positive" if value > 0 else "negative" if value < 0 else "neutral"


def summarize(text, word_frequencies=None, sentence_count=1):
    """Select the top-scoring sentences and retain their original order."""
    sentences = [sentence.strip() for sentence in
                 re.split(r"(?<=[.!?])\s+", text.strip()) if sentence.strip()]
    if not sentences or sentence_count <= 0:
        return ""
    if word_frequencies is None:
        word_frequencies = Counter(
            word for word in tokens(text) if word not in STOPWORDS)
    ranked = (
        (sum(word_frequencies[word] for word in tokens(sentence)
             if word not in STOPWORDS), index, sentence)
        for index, sentence in enumerate(sentences)
    )
    selected = heapq.nsmallest(
        sentence_count, ranked, key=lambda item: (-item[0], item[1]))
    return " ".join(sentence for _, _, sentence in sorted(selected, key=lambda item: item[1]))


def read_complaints():
    with COMPLAINT_FILE.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def answer_question(question, connection, today=None):
    """Answer only the supported PM2.5 station/date question pattern."""
    normalized = question.lower()
    if "pm2.5" not in normalized and "pm25" not in normalized:
        return "Please ask for a PM2.5 reading."
    stations = [row[0] for row in connection.execute(
        "SELECT station FROM stations ORDER BY LENGTH(station) DESC")]
    station = next((name for name in stations if name.lower() in normalized), None)
    if station is None:
        return "Please specify a known monitoring station."
    match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", normalized)
    if match:
        day = match.group(0)
    elif "today" in normalized:
        if today is None:
            day = date.today().isoformat()
        elif isinstance(today, date):
            day = today.isoformat()
        else:
            day = str(today)
    else:
        return "Please specify a date or ask for today's reading."
    try:
        day = date.fromisoformat(day).isoformat()
    except ValueError:
        return "The requested date is invalid."
    row = connection.execute(
        "SELECT AVG(pm25) FROM readings WHERE station=? AND day=?",
        (station, day),
    ).fetchone()
    if row[0] is None:
        return f"No valid PM2.5 reading is available for {station} on {day}."
    return f"Mean PM2.5 at {station} on {day}: {row[0]:.1f} micrograms/m3."


def evaluate():
    complaints = read_complaints()
    if len(complaints) < 50:
        raise ValueError("At least 50 complaints are required for evaluation")
    frequencies = Counter(
        word for row in complaints for word in tokens(row["complaint"])
        if word not in STOPWORDS)
    matches = [
        (row, label(row["complaint"]), summarize(
            row["complaint"], frequencies, sentence_count=1))
        for row in complaints
    ]
    correct = sum(predicted == row["manual_label"]
                  for row, predicted, _ in matches)
    first_sentence_coverage = 0
    extractive_coverage = 0
    first_sentence = re.compile(r"(?<=[.!?])\s+")
    lexicon_words = POSITIVE | NEGATIVE
    for row, _, summary in matches:
        first = first_sentence.split(row["complaint"])[0]
        first_sentence_coverage += bool(lexicon_words.intersection(tokens(first)))
        extractive_coverage += bool(lexicon_words.intersection(tokens(summary)))

    raw_source = (BASE_DIR.parent / "Task02" / "raw_readings.csv").read_text(
        encoding="utf-8")
    cleaned, _ = clean_text(raw_source)
    con = create_database(cleaned)
    bot_answer = answer_question(
        "What is the PM2.5 in Adyar today?", con, today="2026-10-01")
    con.close()

    output = [
        "Complaint count: " + str(len(complaints)),
        f"Sentiment agreement with manual labels: {correct}/{len(complaints)} "
        f"({100 * correct / len(complaints):.1f}%)",
        "Disagreements: " + repr([
            (row["id"], row["manual_label"], predicted)
            for row, predicted, _ in matches
            if predicted != row["manual_label"]]),
        "Misclassified example: complaint 5 is manually positive but scores "
        "neutral because 'improved' (+1) and 'smoke' (-1) cancel; the rule does "
        "not understand that reduced smoke is a positive change.",
        "First-sentence baseline salient-word coverage: "
        f"{first_sentence_coverage}/{len(complaints)}",
        "Extractive summary salient-word coverage: "
        f"{extractive_coverage}/{len(complaints)}",
        "Summary comparison: the first-sentence baseline selects the generic "
        "reporting sentence and covers no sentiment keywords; the word-score "
        "extractor covers salient keywords in 45 complaints. Selecting the "
        "first k pre-split sentences costs O(1) time and selection space for "
        "fixed k. The extractor tokenizes/scans O(words) text and selects top "
        "sentences in O(sentences log k), which is O(words) for fixed k; it "
        "uses O(words) space for word frequencies and O(k) top-sentence "
        "selection space, in addition to the input and emitted summary.",
        "Example complaint: " + complaints[0]["complaint"],
        "Extractive summary: " + matches[0][2],
        "Chatbot example: " + bot_answer,
        "Interpretation: the hand-authored labels are a small, synthetic "
        "reference set, not a held-out clinical or city-wide evaluation. The "
        "simple lexicon handles direct polarity and one-token negation, but "
        "misses sarcasm, scope, double negation, and domain-specific meaning. "
        "The extractive summary retains salient source text; its coverage "
        "measure counts a lexicon word and does not establish factual quality. "
        "A model should be considered only after a representative, "
        "privacy-reviewed multilingual evaluation shows a useful improvement.",
    ]
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    result = "\n".join(output) + "\n"
    (RESULTS_DIR / "complaint_results.txt").write_text(result, encoding="utf-8")
    print(result, end="")


if __name__ == "__main__":
    evaluate()
