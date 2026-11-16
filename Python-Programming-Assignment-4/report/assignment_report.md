# Assignment 4 — Robust data processing report

**Student name:** [Your Name]  
**Register number:** [Your Register Number]  
**Python:** 3.11.0

The sample files and console output in this project were generated with Python
3.11.0. Add your own screenshots or console captures after rerunning the
commands in the README. The report's examples are intended to be checked and
adapted by the student before submission.

## Task 1 — File-processing design review

### Deficiencies and office impact

1. A hard-coded desktop path will fail when the file is on another computer,
   drive, or month.
2. The file is not protected by a context manager; exceptions can leave its
   handle open and prevent later replacement or deletion.
3. `read()` loads all 50,000 lines into memory before processing instead of
   keeping memory near one line plus the output.
4. `except:` catches programming errors, bad data, and operating-system
   failures indiscriminately; `pass` hides every rejected student.
5. `int()` rejects valid paise amounts such as `1250.50` and loses the
   currency's decimal precision.
6. `report = report + ...` repeatedly copies an ever-growing string and does
   not give a structured place to record rejected lines.
7. Splitting the entire string by newline creates an empty final record when
   the file ends in `\n`; treating it as malformed adds false errors.
8. The script does not check the number of fields, so `parts[2]` can raise
   `IndexError`, and it does not explain which line is damaged.

### Repaired design and evidence

`Task01.mess_bills.process_mess_file(file_name)` streams the source with
`with open(...)` and enumerates one line at a time. It uses `csv.reader` for
fields, `Decimal` for exact amounts, specific catches for malformed records,
and a `RejectedLine` list with line numbers and reasons. Missing file,
permission, directory, and UTF-8 decoding errors are reported by the CLI.
For the sample file, the total is **2356.25** and the damaged third line is
recorded as `expected 3 fields, found 2`.

The design defence (under 100 words): The repaired script is safer for
50,000 lines because it closes the input even after failure, reads one line at
a time, and uses `Decimal` rather than truncating paise. Invalid data is
reported with a line number instead of disappearing behind a bare exception.
The output is accumulated as a list and joined only for display. Expected
processing time remains O(n) for n lines; streaming needs O(one line) working
memory rather than O(file size), apart from the retained report and rejected
records.

Using `read()` or `readlines()` still takes O(n) time but holds the whole
file's text (and, for `readlines()`, a list of line objects) in memory.
Iteration over the file takes O(one line) working memory.

## Task 2 — Monthly biometric attendance

### Data and file operations

Each UTF-8 daily file is named `attendance_YYYY-MM-DD.csv`. A nonblank line
contains `register,date,P` or `register,date,A`. The processor keeps
`register -> [present_count, absent_count]` in a dictionary. The percentage
CSV contains register, present, absent, valid-record count, and percentage.
The below-75 CSV contains register and percentage. The damaged-record CSV
contains file name, 1-based line number, original line, and error message.

Input files use mode `r`, UTF-8, and iteration so each line is processed once.
The three output files use mode `w` to replace the current month's reports,
UTF-8, and `csv.writer`/`write`. Append mode `a` is appropriate for a
persistent error log, but not for regenerating monthly summary reports.

### Processing pseudocode and trace

```text
list daily files matching attendance_<month>-*.csv with pathlib
for each file:
    open it as UTF-8 in a with statement
    for each line and line number:
        skip blank lines
        parse fields and validate date/status
        if invalid: append (file, line number, raw line, reason) to errors
        else: increment the student's present or absent count
write all percentage rows
write rows with percentage below 75
write all damaged-line records
```

Trace for `1,2026-10-01,P`, `2,2026-10-01,A`, `bad-line`: student 1 becomes
`[1, 0]`; student 2 becomes `[0, 1]`; the third line has one field instead
of three and is written to the damaged-record report at line 3. Its malformed
content does not change either count.

Re-reading f files of l lines for each of s students costs O(s·f·l) time.
Reading every file once and updating a dictionary costs O(f·l) average time
and O(s) count storage, plus the rejected-line list.

## Task 3 — Exception design

### Failure table

| Failure | Expected exception / handling |
| --- | --- |
| Missing input folder or file | `FileNotFoundError`; wrap as `AttendanceFileError` in `summarise` or log the source in the monthly processor |
| No read permission | `PermissionError`; report the file and preserve the original cause |
| Directory supplied where a file is expected | `IsADirectoryError` |
| Bytes are not valid UTF-8 | `UnicodeDecodeError` |
| Missing or extra fields / invalid status | `InvalidRecord` or `InvalidAttendanceLine` |
| Invalid date in the monthly processor | `ValueError`, converted to `InvalidAttendanceLine` with `raise ... from ...` |
| Empty file | no exception; summary is zero present, zero absent, no bad lines |
| Invalid money text in Task 1 | `decimal.InvalidOperation`, recorded against that line |

`InvalidRecord` is raised by `parse_line` when a row is structurally invalid
or has a status other than `P` or `A`. `summarise` catches it per line so
processing continues, and records `(line_number, message)`. File-level
exceptions are wrapped in `AttendanceFileError` with `raise ... from ...`;
the caller can inspect `__cause__`. The `with` statement closes the file, and
the `finally` block is a last-resort close check.

The completed example prints:

```text
(1, 1, [(3, 'expected 3 fields, found 2'), (4, "invalid status 'L'")])
```

The misuse experiment is equivalent to:

```python
try:
    presnt += 1  # misspelled variable raises NameError
except Exception:
    pass
```

It appears to continue successfully, but the attendance count was never
updated and no diagnostic is visible. Catch the expected exception types and
log or report failures rather than hiding them.

When malformed lines are rare, exceptions are a readable path for exceptional
data and add little normal-path work; when malformed lines are common,
explicit validation avoids repeatedly constructing exceptions and is often
clearer. Both approaches still inspect each line, so asymptotic processing is
O(lines).

## Task 4 — File and exception forensics

Opening `returns.log` with `"w"` truncates earlier days. Writing each book
without `"\n"` joins the records. If `write()` raises before `close()`, the
manual close is skipped and the handle remains open until cleanup.

The tests run three sample days. The flawed implementation leaves only
`'C-301C-302'` in the log: earlier days were overwritten and the last day's
two book IDs are joined. The repaired implementation uses `"a"`, writes one
book plus a newline, protects both input and output with `with`, and records
missing-file/write errors in a separate error log.

Two prevention rules: (1) use a `with` statement for every opened file; (2)
choose `"w"` only for intentional replacement and `"a"` for a continuing
event log, and explicitly write record separators.

Correct manual handling would use `try: ... finally: handle.close()` for every
opened file. With correct `finally`, time and space complexity are unchanged
and at most the same explicitly opened files are active. With `with`, each
context closes deterministically on exit; manual code that omits `finally`
can leave one or more files open after an exception.

## Task 5 — Organizing the attendance utility

Four runnable versions process the same sample and produce the same
percentages and three-day absence report:

1. `single_script/attendance_single.py`: reader, statistics, writer, and main
   in one file.
2. `module_import/attendance_utils.py` plus `main.py`: one reusable module
   imported by a small entry point.
3. `three_modules/reader.py`, `stats.py`, `report.py`, and `main.py`: grouped
   by responsibility.
4. `attendance_package/attendance/`: `__init__.py` exports reader, stats, and
   report functions from separate submodules, with a package `main.py`.

Adding the consecutive-absence report required 1 file in the single-script
version, 2 in the one-module version (utility and main), and 3 in each
multi-module/package version (statistics, report writing, and orchestration).
The one-file version is easiest to start but becomes hard to locate and test.
Modules improve reuse; responsibility-based modules make tests and changes
more focused. Packages provide a clear namespace but need more navigation.

`import attendance.stats` binds the package namespace and is explicit at use
sites; `from attendance import stats` imports the submodule into the current
namespace; `from attendance.stats import percentages` imports the function
directly but can make its origin less obvious and can shadow another name.
Imported modules are cached in `sys.modules`, so later imports in the same
process reuse the module. Package startup has a one-time O(module code) import
cost and stores module objects/code in memory; asymptotic attendance
processing is unchanged.

## Task 6 — College fest registration package

### Requirements and design decisions

Inputs are up to five UTF-8 department files with one CSV row per registration:
register number, name, department, email, semicolon-separated events. The
outputs are a deduplicated `master.csv`, one participant CSV per event,
`summary.txt`, and `errors.log`.

Testable requirements: every valid register number appears once; repeated
registers merge their event sets; an invalid email or damaged row is logged
with file and line but does not stop later rows; a missing department file is
logged and other departments continue; event files contain exactly the
registrants for that event.

Email validation uses string methods: exactly one `@`, nonempty local/domain
parts, no whitespace, a dot in the domain, and no leading/trailing or repeated
domain dot. Duplicate identity is the register number, stored in a set-like
dictionary index. Events are sets, so duplicates within or across department
files disappear. The first valid name/department/email is retained while
events are combined.

Processing flow:

```text
for each expected department file:
    try open UTF-8 file
    if file cannot be opened: append a file-level error and continue
    for each nonblank line:
        parse and validate fields and email
        if invalid: append a line-numbered error and continue
        if register is already known: merge event set and count duplicate
        else: add to master dictionary
write master CSV, event CSVs, summary, and error log
```

Package structure:

```text
Task06/
  run_demo.py
  fest/
    __init__.py
    models.py       Registration and RejectedRecord
    reader.py       read_department_file
    validation.py   valid_email and parse_registration
    merge.py        merge_registrations
    writer.py       write_outputs
    pipeline.py     process_files and process_department_folder
```

The demonstration has clean rows, a duplicate register, invalid email,
damaged fields, and a missing fifth department file. It produces four unique
master registrations, merges one duplicate, and logs three errors. The
alternative list-search method compares each registration against prior
records, O(n²) time; the dictionary/set design is expected O(n) overall for
hash lookups and O(n) storage. The dictionary design is chosen for the
100,000-registration case. A remaining limitation is that the first valid
contact details win if duplicate registration rows disagree; a production
system should log those conflicts explicitly.
