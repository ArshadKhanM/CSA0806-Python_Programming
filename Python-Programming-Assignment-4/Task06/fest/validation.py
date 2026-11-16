"""Validate one registration record and its e-mail address."""

import csv
from io import StringIO

from .models import Registration


class InvalidRegistration(ValueError):
    """A registration row is incomplete or contains invalid fields."""


def valid_email(value: str) -> bool:
    """Validate a basic address using string methods rather than a regex."""
    email = value.strip()
    if not email or any(character.isspace() for character in email) or email.count("@") != 1:
        return False
    local, domain = email.split("@")
    if not local or not domain or "." not in domain:
        return False
    if domain.startswith(".") or domain.endswith(".") or ".." in domain:
        return False
    return True


def parse_registration(line: str) -> Registration:
    """Parse register,name,department,email,event1;event2."""
    try:
        fields = next(csv.reader(StringIO(line)))
    except csv.Error as error:
        raise InvalidRegistration(f"malformed CSV: {error}") from error
    if len(fields) != 5:
        raise InvalidRegistration(f"expected 5 fields, found {len(fields)}")
    register, name, department, email, event_field = (field.strip() for field in fields)
    if not register or not register.isdigit():
        raise InvalidRegistration("register number must contain digits")
    if not name:
        raise InvalidRegistration("name is empty")
    if not department:
        raise InvalidRegistration("department is empty")
    if not valid_email(email):
        raise InvalidRegistration(f"invalid email {email!r}")
    events = {event.strip() for event in event_field.split(";") if event.strip()}
    if not events:
        raise InvalidRegistration("at least one event is required")
    return Registration(register, name, department, email.casefold(), events)
