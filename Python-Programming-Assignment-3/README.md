# Python Programming Assignment 3 — Data Structures

**Student name:** [Mohamed Arshad Khan M ]  
**Register number:** [1965L260001]  
**Python used for validation:** Python 3.11.0 (standard library only)  
**Repository:** https://github.com/ArshadKhanM/CSA0806-Python_Programming

Replace the student placeholders before submission. The runnable solutions
and test files are grouped by question. Measurement output depends on the
machine; rerun the benchmark commands and update the report with your own
results.

## Tasks and commands

| Question | Topic | Run |
| --- | --- | --- |
| Q1 | Rainfall lists, slicing, and moving averages | `python -m Task01.rainfall` |
| Q2 | Tuples, mutability, and copying | `python -m Task02.tuples_copying` |
| Q3 | Dictionary complaint analysis | `python -m Task03.complaints` |
| Q4 | Set-based elective clash reports | `python -m Task04.electives` |
| Q5 | Sensor cleaning and comprehensions | `python -m Task05.sensor_readings` |
| Q6 | Nested railway timetable and station index | `python -m Task06.timetable` |
| Q7 | Contact merging from first principles | `python -m Task07.contacts` |

Run the unit tests from this directory:

```powershell
python -m unittest discover -v
```

Run the larger timing experiments (these may take longer):

```powershell
python -m Task01.rainfall --benchmark
python -m Task02.tuples_copying --benchmark
python -m Task03.complaints --benchmark
python -m Task04.electives --benchmark
python -m Task05.sensor_readings --benchmark
python -m Task06.timetable --benchmark
python -m Task07.contacts --benchmark
```

## Complexity summary

- **Q1:** For n readings and fixed window w=7, weekly totals and moving
  averages are O(n). Naive moving averages sum each window independently,
  doing `(n-w+1)(w-1)` additions. A running sum needs `w-1 + n-w` additions
  plus `n-w` subtractions. An array-backed list supports O(1) indexing;
  inserting in the middle costs O(n).
- **Q2:** Tuple-key lookup and grid indexing are O(1) average. A rectangular
  list-of-lists grid uses O(rows × columns) space. A sparse dictionary of
  occupied `(row, column)` cells uses O(nonempty cells) space. A shallow copy
  duplicates only the outer container; a deep copy recursively duplicates
  nested mutable children.
- **Q3:** Counting n tokens with a dictionary is O(n) average and O(d) space
  for d distinct words. Calling `list.count` once per distinct word is
  O(n × d). `Counter` is a concise dictionary-based alternative.
- **Q4:** Set membership/intersection is O(1) average per lookup / O(n+m)
  average for two sets; nested list comparisons cost O(nm). Sets remove
  duplicate values and do not preserve input order.
- **Q5:** Loop, comprehension, and map/filter conversions are O(n) time.
  Materialized output lists use O(n) memory; a generator uses O(1) iterator
  memory apart from the source and any final aggregate.
- **Q6:** A scan without an index costs O(total stops) per query. A station
  index costs O(trains at that station) to query and requires O(total stops)
  additional references to build/store.
- **Q7:** Number normalization and hash-map grouping are expected O(n) total
  time for n contact records (union-find adds near-constant inverse-Ackermann
  overhead), versus O(n²) pairwise comparison. The index and merged contacts
  use O(n) space.

The analysis and measured evidence are in [`report/assignment_report.md`](report/assignment_report.md).
