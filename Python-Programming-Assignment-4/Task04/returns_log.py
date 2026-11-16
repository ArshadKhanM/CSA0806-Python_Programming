"""Demonstrate the log defects and provide an append-only safe implementation."""

import argparse
import tempfile
from pathlib import Path
from collections.abc import Iterable


def flawed_save_returns(books: Iterable[str], log_path: str | Path) -> None:
    """Intentionally flawed: overwrites the log and adds no line separators."""
    log = open(log_path, "w", encoding="utf-8")
    for book in books:
        log.write(book)
    log.close()


def flawed_process(day_file: str | Path, log_path: str | Path) -> None:
    books = Path(day_file).read_text(encoding="utf-8").split("\n")
    flawed_save_returns(books, log_path)


def _append_error(error_log: str | Path, message: str) -> None:
    with open(error_log, "a", encoding="utf-8") as errors:
        errors.write(message.rstrip("\n") + "\n")


def process_returns(
    day_file: str | Path, log_path: str | Path, error_log: str | Path
) -> bool:
    """Read one day's books, append one per line, and persist expected failures."""
    try:
        with open(day_file, "r", encoding="utf-8") as source:
            books = [line.rstrip("\r\n") for line in source if line.rstrip("\r\n")]
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, IsADirectoryError) as error:
        detail = getattr(error, "strerror", None) or str(error)
        _append_error(error_log, f"{Path(day_file).name}: {type(error).__name__}: {detail}")
        return False

    try:
        with open(log_path, "a", encoding="utf-8", newline="") as log:
            for book in books:
                log.write(book + "\n")
    except OSError as error:
        detail = getattr(error, "strerror", None) or str(error)
        _append_error(error_log, f"{Path(log_path).name}: {type(error).__name__}: {detail}")
        return False
    return True


def demo(directory: Path) -> None:
    day_files = []
    for day, books in enumerate((["A-101", "A-102"], ["B-201"], ["C-301", "C-302"]), start=1):
        source = directory / f"day{day}.txt"
        source.write_text("\n".join(books) + "\n", encoding="utf-8")
        day_files.append(source)

    flawed_log = directory / "flawed.log"
    for source in day_files:
        flawed_process(source, flawed_log)
    print("flawed log after three days:", repr(flawed_log.read_text(encoding="utf-8")))

    safe_log = directory / "returns.log"
    error_log = directory / "errors.log"
    for source in day_files:
        process_returns(source, safe_log, error_log)
    process_returns(directory / "missing.txt", safe_log, error_log)
    print("repaired log:")
    print(safe_log.read_text(encoding="utf-8"), end="")
    print("error log:", error_log.read_text(encoding="utf-8").strip())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if not args.demo:
        parser.error("use --demo to run the temporary-file demonstration")
    with tempfile.TemporaryDirectory() as temporary:
        demo(Path(temporary))


if __name__ == "__main__":
    main()
