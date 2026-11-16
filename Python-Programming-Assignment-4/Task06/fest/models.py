"""Data models shared by the fest-registration package."""

from dataclasses import dataclass, field


@dataclass
class Registration:
    register: str
    name: str
    department: str
    email: str
    events: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class RejectedRecord:
    file_name: str
    line_number: int
    raw_line: str
    reason: str
