"""Attendance file-processing package."""

from .reader import read_rows
from .report import write_reports
from .stats import absent_three_days, percentages

__all__ = ["read_rows", "write_reports", "absent_three_days", "percentages"]
