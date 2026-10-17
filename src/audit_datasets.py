"""Create a reproducible structural and data-quality audit of the raw CSV files.

The script intentionally uses only the Python standard library so the first
project step can run before the modeling environment is installed.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = PROJECT_ROOT / "data" / "raw"
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "step-01" / "dataset_audit.json"
REFERENCE_FILES = {"unclean cclass.csv", "unclean focus.csv"}
AUXILIARY_CLEANED_FILES = {"cclass.csv", "focus.csv"}
DATA1_CORE_FILES = {
    "audi.csv",
    "bmw.csv",
    "ford.csv",
    "hyundi.csv",
    "merc.csv",
    "skoda.csv",
    "toyota.csv",
    "vauxhall.csv",
    "vw.csv",
}
PLACEHOLDER_TOKENS = {"-", "–", "—", "n/a", "na", "null", "unknown", "not available"}
FORMATTED_NUMBER = re.compile(
    r"^[\$£€]?\s*([+-]?\d+(?:\.\d+)?)\s*(?:mi\.?|miles?)?$",
    flags=re.IGNORECASE,
)


def parse_number(value: str) -> float | None:
    """Parse plain, currency-formatted, or mileage-formatted numeric values."""
    candidate = value.strip().replace(",", "")
    if not candidate:
        return None
    match = FORMATTED_NUMBER.fullmatch(candidate)
    return float(match.group(1)) if match else None


def profile_csv(path: Path) -> dict[str, Any]:
    """Profile one CSV without changing its contents."""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            headers = next(reader)
        except StopIteration:
            return {
                "relative_path": path.relative_to(PROJECT_ROOT).as_posix(),
                "size_bytes": path.stat().st_size,
                "headers": [],
                "row_count": 0,
                "malformed_row_count": 0,
                "exact_duplicate_row_count": 0,
                "columns": {},
            }

        missing = [0] * len(headers)
        placeholders = [0] * len(headers)
        whitespace = [0] * len(headers)
        nonempty = [0] * len(headers)
        numeric = [0] * len(headers)
        numeric_min: list[float | None] = [None] * len(headers)
        numeric_max: list[float | None] = [None] * len(headers)
        values = [Counter() for _ in headers]
        seen_rows: set[tuple[str, ...]] = set()
        duplicate_count = 0
        malformed_count = 0
        row_count = 0

        for raw_row in reader:
            row_count += 1
            if len(raw_row) != len(headers):
                malformed_count += 1

            row = (raw_row + [""] * len(headers))[: len(headers)]
            row_key = tuple(row)
            if row_key in seen_rows:
                duplicate_count += 1
            else:
                seen_rows.add(row_key)

            for index, raw_value in enumerate(row):
                stripped = raw_value.strip()
                if not stripped:
                    missing[index] += 1
                    continue

                nonempty[index] += 1
                if stripped.casefold() in PLACEHOLDER_TOKENS:
                    placeholders[index] += 1
                if raw_value != stripped:
                    whitespace[index] += 1
                values[index][stripped] += 1

                parsed = parse_number(stripped)
                if parsed is not None:
                    numeric[index] += 1
                    current_min = numeric_min[index]
                    current_max = numeric_max[index]
                    numeric_min[index] = parsed if current_min is None else min(current_min, parsed)
                    numeric_max[index] = parsed if current_max is None else max(current_max, parsed)

    column_profiles: dict[str, Any] = {}
    for index, header in enumerate(headers):
        nonempty_count = nonempty[index]
        numeric_rate = numeric[index] / nonempty_count if nonempty_count else 0.0
        column_profiles[header] = {
            "missing_count": missing[index],
            "missing_percent": round(100 * missing[index] / row_count, 4) if row_count else 0.0,
            "placeholder_count": placeholders[index],
            "unique_nonempty_count": len(values[index]),
            "leading_or_trailing_whitespace_count": whitespace[index],
            "numeric_parse_percent_of_nonempty": round(100 * numeric_rate, 4),
            "numeric_min": numeric_min[index] if numeric_rate >= 0.95 else None,
            "numeric_max": numeric_max[index] if numeric_rate >= 0.95 else None,
            "top_values": [
                {"value": value, "count": count}
                for value, count in values[index].most_common(5)
            ],
        }

    if path.name.lower() in REFERENCE_FILES:
        role = "reference_unclean"
    elif path.name.lower() in AUXILIARY_CLEANED_FILES:
        role = "auxiliary_cleaned_subset"
    elif path.name.lower() in DATA1_CORE_FILES:
        role = "data1_core_modeling"
    else:
        role = "modeling_candidate"

    return {
        "relative_path": path.relative_to(PROJECT_ROOT).as_posix(),
        "size_bytes": path.stat().st_size,
        "role": role,
        "headers": headers,
        "row_count": row_count,
        "malformed_row_count": malformed_count,
        "exact_duplicate_row_count": duplicate_count,
        "columns": column_profiles,
    }


def projected_overlap(subset_path: Path, parent_path: Path, columns: list[str]) -> dict[str, Any]:
    """Count subset rows whose shared-field projection occurs in a parent file."""
    with parent_path.open("r", encoding="utf-8-sig", newline="") as handle:
        parent_keys = {
            tuple(row[column] for column in columns)
            for row in csv.DictReader(handle)
        }

    with subset_path.open("r", encoding="utf-8-sig", newline="") as handle:
        subset_rows = list(csv.DictReader(handle))

    matching_rows = sum(
        tuple(row[column] for column in columns) in parent_keys
        for row in subset_rows
    )
    return {
        "subset_file": subset_path.relative_to(PROJECT_ROOT).as_posix(),
        "parent_file": parent_path.relative_to(PROJECT_ROOT).as_posix(),
        "shared_columns": columns,
        "subset_row_count": len(subset_rows),
        "matching_row_count": matching_rows,
        "matching_percent": round(100 * matching_rows / len(subset_rows), 4) if subset_rows else 0.0,
    }


def main() -> None:
    csv_paths = sorted(RAW_ROOT.rglob("*.csv"), key=lambda path: path.as_posix().lower())
    if not csv_paths:
        raise SystemExit(f"No CSV files found under {RAW_ROOT}")

    profiles = [profile_csv(path) for path in csv_paths]
    schema_counts = Counter(tuple(profile["headers"]) for profile in profiles)
    shared_columns = [
        "model",
        "year",
        "price",
        "transmission",
        "mileage",
        "fuelType",
        "engineSize",
    ]
    data1_root = RAW_ROOT / "data1"
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "raw_root": RAW_ROOT.relative_to(PROJECT_ROOT).as_posix(),
        "file_count": len(profiles),
        "total_rows_across_files": sum(profile["row_count"] for profile in profiles),
        "schema_count": len(schema_counts),
        "schemas": [
            {"headers": list(headers), "file_count": count}
            for headers, count in schema_counts.items()
        ],
        "data1_overlap_checks": [
            projected_overlap(data1_root / "focus.csv", data1_root / "ford.csv", shared_columns),
            projected_overlap(data1_root / "cclass.csv", data1_root / "merc.csv", shared_columns),
        ],
        "files": profiles,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Audited {len(profiles)} CSV files and {payload['total_rows_across_files']:,} rows.")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
