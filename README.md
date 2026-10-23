# Python Programming Assignment 1

**Objective:** design, implement, and validate an exact-money payment calculator for a village milk co-operative, then extend it for seasonal rates and a ten-day volume bonus.

**Student name:** `[Your Name]`

**Register number:** `[Your Register Number]`

**Python version used for validation:** Python 3.11.0 (standard library only)
**GitHub repository:** `[Add the repository URL after publishing]`

The assignment report, assumptions, algorithms, test evidence, and design discussion are in [`report/assignment_report.md`](report/assignment_report.md).

## Folder structure

```text
Python-Programming-Assignment-1/
├── README.md
├── .gitignore
├── requirements.txt
├── report/
│   └── assignment_report.md
├── Task01/
│   ├── __init__.py
│   └── analysis.md
├── Task02/
│   ├── __init__.py
│   ├── decimal_total.py
│   └── interpreter_session.txt
├── Task03/
│   ├── __init__.py
│   └── constants.py
├── Task04/
│   ├── __init__.py
│   └── expressions.py
├── Task05/
│   ├── __init__.py
│   └── input_validation.py
├── Task06/
│   ├── __init__.py
│   └── payment_functions.py
├── Task07/
│   ├── __init__.py
│   ├── milkrate.py
│   └── test_milkrate.py
├── Task08/
│   ├── __init__.py
│   ├── flowchart.mmd
│   └── pseudocode.txt
├── Task09/
│   ├── __init__.py
│   ├── milk_calculator.py
│   ├── test_milk_calculator.py
│   └── test_results.txt
├── Task10/
│   ├── __init__.py
│   ├── benchmark.py
│   └── benchmark_results.txt
├── Task11/
│   ├── __init__.py
│   └── recommendation.md
└── Task12/
    ├── __init__.py
    ├── challenge_tests.txt
    ├── seasonal_milkrate.py
    └── test_seasonal_milkrate.py
```

The supplied reference PDF is retained at the project root and is not part of the source-code dependencies.

## Installation and execution

1. Install Python 3.11 or newer and open a terminal in the project root.
2. No third-party packages need to be installed.
3. Run the Task 9 sample collection:

   ```powershell
   python -m Task09.milk_calculator --demo
   ```

4. Run the interactive collection calculator:

   ```powershell
   python -m Task09.milk_calculator
   ```

5. Run the Task 7 module demonstration:

   ```powershell
   python -m Task07.milkrate
   ```

6. Run the Task 12 seasonal demonstration:

   ```powershell
   python -m Task12.seasonal_milkrate
   ```

## Tests

Run all automated unit tests from the project root:

```powershell
python -m unittest discover -v
```

The suite checks valid payments, limits, malformed and non-finite inputs, shift validation, rounding, seasonal selection, and the strict 500-litre bonus boundary.

## Benchmark

Run the Decimal-versus-float benchmark for 300, 6,000, and 150,000 payments:

```powershell
python -m Task10.benchmark
```

The measured output is machine- and interpreter-dependent. `Task10/benchmark_results.txt` contains the output captured when this submission was run; rerun the command on the submission machine for its timings.

## GitHub

Repository URL placeholder: `[Add the actual GitHub repository URL here after creation]`.

To export the report as PDF when a Markdown-to-PDF tool is available, open `report/assignment_report.md` in a Markdown editor and use its PDF export/print function. No PDF-generation dependency is required by this project.
