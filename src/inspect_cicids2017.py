from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect CICIDS2017 CSV files and summarize their contents."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory containing CICIDS2017 CSV files. Defaults to data/raw.",
    )
    parser.add_argument(
        "--limit-files",
        type=int,
        default=None,
        help="Optional limit on the number of CSV files to inspect.",
    )
    return parser.parse_args()


def find_csv_files(data_dir: Path) -> list[Path]:
    return sorted(path for path in data_dir.rglob("*.csv") if path.is_file())


def resolve_label_column(fieldnames: list[str]) -> str | None:
    normalized = {name.strip().lower(): name for name in fieldnames}
    for candidate in ("label", " label"):
        if candidate in normalized:
            return normalized[candidate]
    return None


def inspect_csv(csv_path: Path) -> dict:
    row_count = 0
    label_counts: Counter[str] = Counter()

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row.")

        fieldnames = [name.strip() for name in reader.fieldnames]
        label_column = resolve_label_column(reader.fieldnames)

        for row in reader:
            row_count += 1
            if label_column is not None:
                raw_label = row.get(label_column, "")
                label = raw_label.strip() if raw_label is not None else ""
                label_counts[label] += 1

    return {
        "path": csv_path,
        "rows": row_count,
        "columns": len(fieldnames),
        "fieldnames": fieldnames,
        "label_column": label_column.strip() if label_column else None,
        "label_counts": label_counts,
    }


def print_summary(summary: dict) -> None:
    print(f"\nFile: {summary['path']}")
    print(f"Rows: {summary['rows']:,}")
    print(f"Columns: {summary['columns']}")
    print("First columns: " + ", ".join(summary["fieldnames"][:8]))

    if summary["label_column"] is None:
        print("Label column: not found")
        return

    print(f"Label column: {summary['label_column']}")
    if not summary["label_counts"]:
        print("Label distribution: no rows found")
        return

    print("Top labels:")
    for label, count in summary["label_counts"].most_common(10):
        safe_label = label or "<empty>"
        print(f"  {safe_label}: {count:,}")


def main() -> int:
    args = parse_args()
    data_dir = args.data_dir.resolve()

    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        print("Create it and place the CICIDS2017 CSV files there first.")
        return 1

    csv_files = find_csv_files(data_dir)
    if args.limit_files is not None:
        csv_files = csv_files[: args.limit_files]

    if not csv_files:
        print(f"No CSV files found under: {data_dir}")
        return 1

    print(f"Inspecting {len(csv_files)} CSV file(s) under {data_dir}")
    for csv_file in csv_files:
        summary = inspect_csv(csv_file)
        print_summary(summary)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
