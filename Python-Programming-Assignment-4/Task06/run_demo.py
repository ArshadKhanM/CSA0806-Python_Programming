"""Run the fest package against the included five-department sample."""

from pathlib import Path

from Task06.fest.pipeline import process_department_folder


def main() -> None:
    root = Path(__file__).parent
    result = process_department_folder(root / "sample_input", root / "sample_output")
    print(
        f"master={len(result['master'])}, duplicates={result['duplicates']}, "
        f"errors={len(result['errors'])}"
    )
    print("outputs:", result["outputs"])


if __name__ == "__main__":
    main()
