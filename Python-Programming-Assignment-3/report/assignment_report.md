# Assignment 3 — Data Structures report

**Student name:** [Your Name]  
**Register number:** [Your Register Number]  
**Python:** 3.11.0

The measurements below are from one run on the preparation computer and are
machine-dependent. Re-run the commands in the README and replace the recorded
times with your own before submission. `sys.getsizeof` reports shallow
container size; it does not include the objects referenced by a container.

## Q1 — Lists and rainfall slices

### Design and sample results

The list stores one value per day, so integer day positions directly identify
readings. `weekly_totals` slices seven readings at a time and includes a final
partial week if the year length is not divisible by seven. Wettest/driest
positions and dry days are reported as 1-based day numbers.

Moving-average pseudocode:

```text
if fewer than 7 readings: return []
running = sum(first 7 readings)
append running / 7
for each new day i from 7 to n-1:
    running = running - reading[i-7] + reading[i]
    append running / 7
```

For a 365-reading list, the program reports **2,154** additions for naive
seven-value sums versus **364** additions for the running sum (plus 358
subtractions). At 36,500 readings the counts are 218,964 versus 36,499; at
365,000 they are 2,189,964 versus 364,999.

For readings of length 365, `readings[7:14]` selects indices 7 through 13,
`readings[-7:]` selects the last seven values, and `readings[::7]` selects
every seventh value starting at index 0; the last slice is not a weekly sum.
`append` is O(1) amortized, `insert` and `pop(i)` are O(n) away from the end,
`pop()` at the end is O(1) amortized, and `sort` is O(n log n). Late insertion
at a date costs O(n) because later list elements must shift; a list remains
suitable for a modest year of daily readings.

### Timing

| Readings | Naive moving average | Running sum |
| ---: | ---: | ---: |
| 365 | 0.000081 s | 0.000039 s |
| 36,500 | 0.008755 s | 0.003833 s |
| 365,000 | 0.087792 s | 0.045337 s |

Both approaches are O(n) when the window width is the fixed constant 7, but
the running method performs fewer additions. With a variable window width w,
the naive method performs O(nw) work, while a running sum remains O(n).
A `deque(maxlen=7)` provides O(1) end updates and constant window storage;
date-keyed dictionary access is O(1) average but chronological moving
averages still need ordered dates/iteration.

## Q2 — Tuples, mutability, and copying

The bad grid has three references to one row:

```text
bad -> [row, row, row] -> [0, 0, 0, 0]
```

The corrected comprehension creates independent row objects:

```text
good -> [row0, row1, row2]
        row0 -> [0, 0, 0, 0]
        row1 -> [0, 0, 0, 0]
        row2 -> [0, 0, 0, 0]
```

The demo confirms `bad[0] is bad[1]` is true and `good[0] is good[1]` is
false. Coordinate tuples work as dictionary keys because their contents are
hashable; lists are mutable and therefore unhashable. A tuple that contains a
list is itself immutable, but the contained list can still change.

Both `copy.copy` and slicing duplicate only the outer list. The inner lists
remain aliased, so a change to an inner list is visible through each shallow
copy. `copy.deepcopy` recursively copies the inner lists. A function that
mutates a passed list acts on the same list object held by the caller.

For one million integers, shallow container sizes measured **8,000,056 bytes**
for a list and **8,000,040 bytes** for a tuple. Creation measured 0.039212 s
for a list and 0.034263 s for a tuple. Direct-index timings were 0.00000218 s
and 0.00001248 s respectively in this short run; such tiny differences are
noise-prone. A tuple is appropriate for a fixed coordinate pair and protects
the key from reassignment; use a list when the collection itself must grow or
change.

The sparse-grid alternative stores only nonzero passenger counts under
`(row, column)` keys. Dictionary lookup is O(1) average, as is list indexing;
the dense grid uses O(rows × columns) space while the sparse mapping uses
O(number of occupied cells).

## Q3 — Farmer complaint dictionaries

The tokenizer lowercases text and removes punctuation before counting. The
`get()` and `setdefault()` implementations produce identical frequencies;
the sample top three are:

```text
[('seeds', 3), ('price', 2), ('received', 2)]
```

`price` precedes `received` because equal counts are sorted alphabetically.
The dictionaries also group complaint texts by district and crop. Empty text
returns no tokens, and case/punctuation variants normalize to the same word.

A dictionary hashes a key to find its bucket. Lookup is O(1) average (with
possible O(n) worst case under severe collisions). Counting n tokens with d
distinct words takes O(n) average time and O(d) space; repeatedly calling
`list.count` for each distinct word takes O(n × d). `Counter` is a standard
library dictionary-based implementation. Dict insertion order is guaranteed
from Python 3.7. `keys()`, `values()`, and `items()` are dynamic views over
the dictionary, not copies.

| Complaints | `get()` dictionary | `list.count()` | `Counter` |
| ---: | ---: | ---: | ---: |
| 1,000 | 0.001593 s | 0.003380 s | 0.001347 s |
| 10,000 | 0.013989 s | 0.023610 s | 0.015431 s |
| 100,000 | 0.157783 s | 0.383339 s | 0.134212 s |

For 100,000 complaints, `Counter` or the explicit dictionary loop is the
deployment choice; both scale linearly on average. The list-count method is
included for comparison, not deployment.

## Q4 — Elective sets

For the supplied small case, intersection (`&`) yields
`192311004, 192311009`; symmetric difference (`^`) yields
`192311001, 192311002, 192311007, 192311010`; and subtracting the union from
all students yields `192311003, 192311005, 192311006, 192311008`. The operator
and set-method implementations produce the same sorted reports.

Venn interpretation: the intersection is the overlap; symmetric difference
is the two non-overlapping lobes; `all_students - (first | second)` is outside
both circles. Sets automatically discard duplicates and do not retain
registration order. Membership in a set is O(1) average versus O(n) for a
list scan. Lists cannot be set members because they are mutable/unhashable;
tuples whose elements are hashable can.

Membership measurements (target is the last value in each collection):

| Register numbers | List membership | Set membership |
| ---: | ---: | ---: |
| 10,000 | 0.00012067 s | 0.00000043 s |
| 100,000 | 0.00539161 s | 0.00000118 s |
| 1,000,000 | 0.030428 s | 0.00001580 s |

For a 2,000-by-2,000 common-student example, nested comparison took 0.085764 s
and set intersection 0.000363 s in one run. Nested loops are O(nm);
sorting both lists then walking them is O(n log n + m log m); set operations
are O(n+m) average with storage for the sets/results. Convert to a set when
membership, duplicate removal, or overlap matters; doing so loses duplicate
counts and original order.

## Q5 — Sensor readings and comprehensions

The valid range is inclusive `-50 <= C <= 50`; Fahrenheit is
`C * 9 / 5 + 32`. Alarm positions refer to the original zero-based minute
indices where a valid reading is below 2 C or above 8 C. The loop,
comprehension, and map/filter implementations return identical results for
valid, invalid, and mixed input.

General form: `[expression for item in iterable if condition]`. A comprehension
is clear for one simple transformation/filter; a loop is easier to read when
there are multiple side effects or nested conditions. A dictionary
comprehension maps minute to valid value; a set comprehension collects
distinct valid values. A generator expression computes values lazily and
doesn't allocate a result list.

| Readings | Loop | Comprehension | map/filter |
| ---: | ---: | ---: | ---: |
| 10,000 | 0.002480 s | 0.002589 s | 0.003546 s |
| 100,000 | 0.028046 s | 0.025682 s | 0.035889 s |
| 1,000,000 | 0.309340 s | 0.442497 s | 0.481316 s |

For one million generated readings, `sys.getsizeof` reported a **6,675,480**
byte list container and a **216** byte generator. The list's referenced
temperature objects are additional memory. All methods take O(n) time.
Comprehensions are not always fastest; use the clearest method for the
problem, and use a generator when streaming or aggregating without needing
all converted values at once.

## Q6 — Railway timetable and index

Each train number maps to a record containing a name, a list of stop tuples
`(station, arrival, departure)`, and a set of running days. Dictionaries make
train lookup direct; lists preserve route order; tuples keep each stop's
three fields together; sets support day membership. The third stop's
departure is `timetable[train_number]["stops"][2][2]`.

The scan and indexed queries return the same departure-sorted results. An
unknown station and a train not running on the requested day return no
result. Without an index, a query scans O(total stops). Building
`station -> [train numbers]` costs O(total stops) time and space; after that,
a query checks only trains serving that station, O(station stops + matches).
The index therefore reduces repeated query work at the cost of memory and
maintenance when schedules change. A flat `(train, station, arrival,
departure, days)` list is simpler but needs O(total stops) per query and does
not avoid repeated scans.

| Trains | Scan/query | Indexed/query | Shallow index containers |
| ---: | ---: | ---: | ---: |
| 100 | 0.000025 s | 0.000003 s | 10,784 bytes |
| 1,000 | 0.000247 s | 0.000042 s | 73,184 bytes |
| 10,000 | 0.005930 s | 0.000770 s | 719,584 bytes |

The index byte count includes the dictionary and station train-number lists,
not the referenced strings or timetable itself.

## Q7 — Contact merging from first principles

### Requirements and design

Input is a collection of contacts with an optional name, phone number(s), and
email(s). Output is one record for each connected group of contacts sharing
at least one normalized phone number, including all observed names, unique
numbers, and unique email addresses. Phone formatting is normalized to digits;
a leading `91` country prefix is removed from 12-digit values. Names are
case-folded for comparison/display metadata but are not used as identity:
two people with the same name and different numbers remain separate.

Pseudocode:

```text
for each input contact:
    normalize its phone numbers; make one component for this record
    look up each number in number_to_contact
    union this component with every matching component
    add the contact's numbers, emails, and names to the merged component
    map each number to the component
return each distinct component
```

The dictionary supplies expected O(1) average number lookup; union-find
combines transitive matches. Total work is near-linear O(n α(n)) for n
contacts, plus the number/email set updates; memory is O(n). A nested
pairwise implementation scans earlier records and is O(n²). It is practical
as a baseline on 1,000 records, not 100,000.

| Contacts | Dictionary/union-find | Pairwise | Merged contacts |
| ---: | ---: | ---: | ---: |
| 1,000 | 0.006745 s | 0.027463 s | 500 |
| 100,000 | 1.573735 s | not run (about 10,000,000,000 pair comparisons) | 50,000 |

The small example merges `Dr. Ravi`, `ravi kumar`, and `Ravi` by shared
normalized phone numbers, including a contact that bridges two existing
groups. The same-name/different-number test remains separate, and missing
phone/email fields are accepted. One limitation is that people with no
shared phone number are not merged, even if names or emails match; conversely,
a family-shared phone number can incorrectly merge different people. This
rule should be reviewed before using the program as a real contacts database.
