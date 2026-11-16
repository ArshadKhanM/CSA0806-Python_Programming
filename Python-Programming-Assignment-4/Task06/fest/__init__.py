"""Package that validates, merges, and reports fest registrations."""

from .pipeline import process_files, process_department_folder
from .validation import InvalidRegistration, parse_registration, valid_email

__all__ = [
    "InvalidRegistration",
    "parse_registration",
    "process_files",
    "process_department_folder",
    "valid_email",
]
