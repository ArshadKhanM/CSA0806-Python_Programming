# Part A — Data and Program Design

**Case study:** City air-quality monitoring network  
**Student:** Mohamed Arshad Khan M  
**Register number:** 1965L260001

## A1 — Data acquisition

### A1.1 Source inspection

Each daily station CSV has one header and one row per station, date, and
hour. The expected columns are `station,date,hour,pm25,pm10,no2,temperature,
temperature_unit`. Numeric readings may be blank or `NA`. Example:

```csv
station,date,hour,pm25,pm10,no2,temperature,temperature_unit
Adyar,2026-10-01,0,48,72,18,77,F
```

Expected row-level problems are blank/`NA` readings (PM2.5 is empty);
negative readings (`pm10=-5`); sensor spikes beyond the plausible range
(`pm25=1200`); Fahrenheit instead of Celsius (`77 F`); duplicate
station/date/hour rows; inconsistent station spelling/case (`" adyar "` vs
`"Adyar"`); invalid dates or hours (`2026-02-30`, hour `24`); short/malformed
rows; and out-of-order records. The B1 fixture contains examples of each.
File-level conditions (missing headers/columns, wrong delimiters, incompatible
encodings, and an empty file) are separately challenged in B2.

### Acquisition and cleaning pseudocode

```text
ALGORITHM AcquireCleanStore
INPUT: daily station CSV files, SQLite database
OUTPUT: cleaned readings, cleaning audit, query results, charts
BEGIN
    DECLARE seen_keys as empty set
    DECLARE station_history and station_medians
    FOR EACH input_file IN daily station CSV files DO
        OPEN input_file using UTF-8 and CSV reader
        VALIDATE required column names
        FOR EACH input_row IN input_file DO
            IF row shape, station, date, hour, or unit is invalid THEN
                INCREMENT malformed-row count
                CONTINUE
            END IF
            NORMALIZE station and date; convert hour to integer
            IF station/date/hour key is already in seen_keys THEN
                INCREMENT duplicate count
                CONTINUE
            END IF
            ADD key to seen_keys
            CONVERT Fahrenheit temperature to Celsius when required
            FOR EACH measurement DO
                IF measurement is missing THEN mark for imputation
                ELSE IF measurement is outside its valid range THEN mark NULL
                ELSE retain measurement and update station history
                END IF
            END FOR
            APPEND normalized row to cleaned rows
        END FOR
    END FOR
    SORT cleaned rows by station, date, and hour
    FILL missing measurements from previous valid value, else station median
    CREATE stations and readings tables and station/date index
    INSERT station and reading rows with parameterized executemany calls
    RUN three parameterized analysis queries
    GENERATE labelled trend, station, scatter, and hourly charts
    WRITE cleaned data, audit, query results, and interpretations
END
```

### A1.2 SQLite storage design

| Table | Column | SQLite type | Key / rule |
| --- | --- | --- | --- |
| `stations` | `station` | TEXT | Primary key, trimmed title case |
| `stations` | `source_temp_unit` | TEXT | `C` or `F`; source metadata |
| `readings` | `station` | TEXT | Foreign key to `stations.station` |
| `readings` | `day` | TEXT | ISO `YYYY-MM-DD` |
| `readings` | `hour` | INTEGER | 0-23 |
| `readings` | `pm25`, `pm10`, `no2`, `temperature_c` | REAL | NULL where invalid/unavailable |

`readings` has composite primary key `(station, day, hour)` and an index on
`(station, day)`. The station name maps to `stations.station`; date maps to
`readings.day`; hour maps to `readings.hour`; each pollutant maps to its
same-named REAL column; and temperature is converted to Celsius before it
maps to `temperature_c`. A missing value is stored as SQL NULL. Parameterized
inserts and queries keep text values separate from SQL syntax.

### A1.3 CSV or SQL?

1. **One station's October PM2.5 mean:** scan every CSV and filter rows in
   Python, or use `SELECT AVG(pm25) FROM readings WHERE station=? AND
   day>=? AND day<?`. With a `(station, day)` index, the query can seek to the
   requested station/date range rather than repeatedly parsing every file.
2. **Compare station monthly means:** load and group all CSV rows, or use
   `SELECT station, AVG(pm25) ... GROUP BY station`. SQL expresses the
   aggregation near the stored data and can reuse the index.
3. **Find the worst reporting hours:** parse and group the CSVs in Python,
   or group by `hour` and order by `AVG(pm25)` in SQLite.

CSV plus pandas is convenient for a one-off exploration and has no database
setup, but each question rereads/parses the files in O(n) time and may load
O(n) records into memory. SQLite costs an initial O(n) ingest and disk space;
an indexed lookup is about O(log n + k) for k matching rows, while a full
aggregate still has to inspect its matching rows. SQLite is the repeatable
choice for daily queries and constraints; CSV remains the interoperable
source/archive format.

If CSVs were the only storage, each query would use `pandas.read_csv` on the
station files, parse dates, filter/group, then discard the DataFrame. That is
O(n) time per question, O(n) peak memory for the loaded rows, and low
additional storage beyond the CSVs. An index avoids the repeated full scan
but adds storage and ingest/maintenance cost.

## A2 — Cleaning and normalization

### A2.1 Rules

- Blank or `NA`: for a missing reading only, use the previous valid reading
  for that station/metric; when no previous reading exists, use that
  station's median valid value. Leave it NULL if the station has no valid
  value. This preserves a continuous series without borrowing another
  station's measurements.
- Negative or out-of-range readings: reject that measurement (store NULL);
  never carry a sensor fault forward as if it were a valid observation.
  PM2.5/PM10 must be 0-999, NO2 0-2000, and Celsius temperature -50 to 60.
- Duplicate `(station,date,hour)`: retain the first source row and count later
  copies as duplicates, ensuring one primary-key reading per hour.
- Fahrenheit: convert to Celsius using `(F - 32) * 5 / 9` before range
  validation and storage.

### A2.2 Normalization

For PM2.5 values `x`, min-max scaling is `(x - min(x)) / (max(x) - min(x))`;
it maps the selected batch to [0,1] and is useful for scale-sensitive
comparisons, but an outlier changes both endpoints. If all values are equal,
define the normalized result as 0. Z-score standardization is
`(x - mean(x)) / population_standard_deviation(x)`; it centers the data and
expresses deviations in standard-deviation units, which is useful for
statistical methods, but is sensitive to outliers and has no fixed range.
Define z-scores as 0 when the standard deviation is zero. Compute either
normalization on valid values only and retain the original PM2.5 column.

If missing records were dropped instead, daily means would use fewer
observations and could be biased when missingness depends on pollution or
weather. Filtering missing values is O(n) time and O(1) extra space in a
streaming pass. Forward fill is O(n) time and O(1) per-station state; a
station-median fallback takes O(n log n) time by sorting the valid values and
O(n) storage if all values are retained (or O(n) time with a selection
algorithm).

### A2.3 Formats

Use ISO date `YYYY-MM-DD`, hour as integer 0-23, station names trimmed with
internal whitespace collapsed and title-cased, and numeric readings as
finite decimal values in canonical units. Missing values are CSV blanks and
SQL NULL, never strings such as `"NA"` in the cleaned dataset.

## A3 — Analysis and visualisation

| Board question | Chart | Reason |
| --- | --- | --- |
| PM2.5 trend during a month | Line chart, date on x-axis | Shows order and changes over time |
| Compare station averages | Bar chart | Makes station categories and their mean levels easy to compare |
| Temperature/PM2.5 relationship | Scatter plot | Shows paired observations, clusters, and possible association |
| Worst hours | Bar chart of hourly means, sorted by hour | Makes differences between the 24 hour categories readable |

A box plot is a useful complementary station distribution/outlier view; a
histogram shows the overall PM2.5 distribution. Every chart has a title,
units, labelled axes, and a note that invalid/missing values are excluded.

Daily summary schema: `(station TEXT, day TEXT, pm25_min REAL, pm25_max REAL,
pm25_mean REAL, valid_count INTEGER)`, with `(station, day)` as the primary
key. Produce it with `SELECT station, day, MIN(pm25), MAX(pm25), AVG(pm25),
COUNT(pm25) FROM readings GROUP BY station, day`; SQLite's aggregate
functions ignore NULL. Python loops have O(n) time and O(stations x days)
dictionary state; SQL GROUP BY also processes n rows, while the database
engine manages grouping/index/temp storage without materializing all input
rows as Python objects. Keeping a running sum/count dictionary is also O(n)
time and O(stations x days) space; retaining every observation and then
calling `statistics.mean` is O(n) time but O(n) reading storage. For repeated
reports, persist the summary table and refresh affected days.

## A4 — Debugging and profiling

During development, temporary `print` calls inspect a small raw row, its
normalized values, and the reason it is rejected. Assertions check invariants
such as unique station/day/hour keys and Celsius bounds. The `logging`
module records counts and warnings with levels so debug details can be
disabled or routed to a file. Set a breakpoint with `pdb` (or the IDE
debugger) before validation, inspect the row and local values, and step over
the unit conversion and imputation branches.

Use `time.perf_counter()` around end-to-end stages for elapsed time;
`timeit` repeats small isolated operations to reduce timing noise; and
`cProfile` ranks function call counts and cumulative time on a representative
dataset. Profile separately from chart display and include input size and
hardware/runtime context in recorded results.

Thousands of synchronous prints can dominate a short run through formatting
and console I/O. Logging can be disabled by raising the configured level;
debugger breakpoints can be removed/disabled and assertions can be left as
cheap correctness checks. Prints have no built-in level/filter and require
manual deletion or guarding. Measure rather than assume the overhead:
`timeit` can compare a quiet loop with an instrumented one.

## A5 — Citizen complaint AI application

### A5.1 Sentiment and summary

Tokenize lowercase words and score positive lexicon matches as +1 and
negative matches as -1. If the immediately preceding token is a negator
(`not`, `never`, `no`), flip that token's score. The sign of the total gives
positive, negative, or neutral. Split a complaint into sentences, remove
common stop words, count important word frequencies, score each sentence by
the frequencies of its important words, and return the top sentences in
their original order. This is extractive: selected text is not rewritten.

### A5.2 Rule-based chatbot

Recognize PM2.5 and common intent words, match a known station name, resolve
`today` from a supplied/current date or parse an ISO date, then execute a
parameterized SQLite query for that station/day. Return a clear no-data or
clarification response when the station/date/measurement is absent. It does
not understand arbitrary phrasing, misspellings, multilingual complaints,
context, units in source text, or ambiguous station names; it must not make
up missing readings.

A trained Naive Bayes model would learn word/label probabilities from
annotated complaints and needs training/evaluation data, preprocessing and
model storage. Prediction is roughly proportional to vocabulary features per
complaint and model memory grows with learned vocabulary/classes. A compact
model is faster and lighter than a large pre-trained language model; either
may improve on a word list for word combinations, but sarcasm, domain shift,
and multilingual content still require representative labels and measured
validation. The small lexicon is O(words) time and O(1) fixed lexicon space;
a trained model adds model memory and inference cost but may offer better
context-sensitive accuracy.

On the 50 synthetic complaints, the scorer agrees with 49 manual labels
(98%); this is not a representative held-out evaluation. A first-k summary
selects a generic opening sentence and covers no salient sentiment words in
this fixture, while the frequency-ranked extractive summary covers such a word
in 45 of 50. Selecting the first k pre-split sentences costs O(1) time and
selection space for fixed k. The word-frequency extractor scans O(words) text
and uses O(words) frequency storage; with fixed k, top-sentence selection is
also O(words) overall.
