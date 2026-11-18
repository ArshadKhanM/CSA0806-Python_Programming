# Python Programming Assignment 5 — Data Acquisition, Cleaning, Analysis and AI

**Student name:** Mohamed Arshad Khan M  
**Register number:** 1965L260001  
**Python used for validation:** Python 3.11.0  
**Assignment GitHub repository:** Create
`CSA08-1965L260001-Assignment5` and paste its URL here before submission.

This folder contains the Part A design and runnable Part B evidence for the
city air-quality case study. Data and measurements are synthetic and
deterministic; benchmark timings are machine-specific. Re-run the commands
below on the submission machine and attach the requested screenshots/report
evidence before submitting.

## Requirements

Install the optional analysis and chart libraries with:

```powershell
python -m pip install -r requirements.txt
```

The pipeline, SQLite examples, tests, sentiment scorer, chatbot, and standard
library benchmark work with Python 3.11.0. pandas and matplotlib are used for
the comparative group-by and charts. Installed versions used for the initial
run are recorded in `requirements.txt`.

## Tasks and run commands

Run commands from this directory.

| Folder | Assignment work | Command |
| --- | --- | --- |
| `Task01` | Part A1-A5 designs, pseudocode, choices, and complexity analysis | Read `Task01/design_report.md` |
| `Task02` | B1 cleaning, exact completed code, SQLite, queries, charts, tests | `python -m Task02.cleaning_pipeline` |
| `Task03` | B2 malformed inputs, SQL injection demonstration, sentiment edge cases, completed SQL code | `python -m Task03.adversarial_checks` |
| `Task04` | B3 loops/pandas/SQL comparison and profiling; B4 index timing and scale decision | `python -m Task04.benchmark_analysis` |
| `Task05` | B4 sentiment, extractive summary, chatbot, and 50-complaint evaluation | `python -m Task05.complaint_ai` |

Run all tests from this directory:

```powershell
python -m unittest discover -v
```

Generated console evidence and charts are saved in each task's `results`
folder. `Task02/raw_readings.csv` is the deliberately messy cleaning input;
`Task05/complaints.csv` contains the 50 annotated example complaints.

## Submission checklist

- Replace/add your own screenshots of the executed tasks and include your
  working GitHub assignment-repository URL on the report cover page.
- Create/share the required `CSA08-<RegisterNumber>-Assignment5` GitHub
  repository with the faculty. This local project does not publish or commit
  files to GitHub.
- Commit work progressively (at least one task per commit) when transferring
  this folder to the required submission repository.
