"""Clean and combine the nine core files in the UK used-car dataset.

Raw files are never modified. Auxiliary Focus/C-Class files are deliberately
excluded because they substantially overlap the broader Ford/Mercedes files.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_ROOT = PROJECT_ROOT / "data" / "raw" / "data1"
OUTPUT_CSV = PROJECT_ROOT / "data" / "processed" / "data1_cleaned.csv"
SUMMARY_JSON = PROJECT_ROOT / "outputs" / "step-01" / "data1_preprocessing_summary.json"

CORE_FILES = {
    "audi.csv": "Audi",
    "bmw.csv": "BMW",
    "ford.csv": "Ford",
    "hyundi.csv": "Hyundai",
    "merc.csv": "Mercedes-Benz",
    "skoda.csv": "Skoda",
    "toyota.csv": "Toyota",
    "vauxhall.csv": "Vauxhall",
    "vw.csv": "Volkswagen",
}

OUTPUT_COLUMNS = [
    "brand",
    "model",
    "year",
    "price",
    "transmission",
    "mileage",
    "fuel_type",
    "tax",
    "mpg",
    "engine_size",
    "engine_size_missing",
]

MIN_YEAR = 1970
MAX_YEAR = 2020


class RejectedRow(ValueError):
    """Raised when a raw record violates a required cleaning rule."""


def required_text(value: str | None, field: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        raise RejectedRow(f"missing_{field}")
    return cleaned


def required_int(value: str | None, field: str) -> int:
    cleaned = required_text(value, field)
    try:
        number = float(cleaned)
    except ValueError as error:
        raise RejectedRow(f"invalid_{field}") from error
    if not number.is_integer():
        raise RejectedRow(f"non_integer_{field}")
    return int(number)


def required_float(value: str | None, field: str) -> float:
    cleaned = required_text(value, field)
    try:
        return float(cleaned)
    except ValueError as error:
        raise RejectedRow(f"invalid_{field}") from error


def normalize_row(raw: dict[str, str], brand: str) -> dict[str, Any]:
    """Normalize one raw row and apply defensible record-level rules."""
    year = required_int(raw.get("year"), "year")
    if year < MIN_YEAR or year > MAX_YEAR:
        raise RejectedRow("year_outside_1970_2020")

    price = required_int(raw.get("price"), "price")
    if price <= 0:
        raise RejectedRow("nonpositive_price")

    mileage = required_int(raw.get("mileage"), "mileage")
    if mileage < 0:
        raise RejectedRow("negative_mileage")

    tax_key = "tax" if "tax" in raw else "tax(£)"
    tax = required_float(raw.get(tax_key), "tax")
    mpg = required_float(raw.get("mpg"), "mpg")
    engine_size = required_float(raw.get("engineSize"), "engine_size")
    engine_size_missing = int(engine_size == 0)

    return {
        "brand": brand,
        "model": required_text(raw.get("model"), "model"),
        "year": year,
        "price": price,
        "transmission": required_text(raw.get("transmission"), "transmission"),
        "mileage": mileage,
        "fuel_type": required_text(raw.get("fuelType"), "fuel_type"),
        "tax": tax,
        "mpg": mpg,
        "engine_size": "" if engine_size_missing else engine_size,
        "engine_size_missing": engine_size_missing,
    }


def row_key(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(row[column]) for column in OUTPUT_COLUMNS[:-1])


def preprocess() -> dict[str, Any]:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)

    seen: set[tuple[str, ...]] = set()
    cleaned_rows: list[dict[str, Any]] = []
    rejected_reasons: Counter[str] = Counter()
    per_file: list[dict[str, Any]] = []

    for filename, brand in CORE_FILES.items():
        input_path = INPUT_ROOT / filename
        if not input_path.exists():
            raise FileNotFoundError(f"Missing required input file: {input_path}")

        raw_count = 0
        accepted_count = 0
        duplicate_count = 0
        file_rejections: Counter[str] = Counter()

        with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for raw in csv.DictReader(handle):
                raw_count += 1
                try:
                    cleaned = normalize_row(raw, brand)
                except RejectedRow as error:
                    reason = str(error)
                    rejected_reasons[reason] += 1
                    file_rejections[reason] += 1
                    continue

                key = row_key(cleaned)
                if key in seen:
                    duplicate_count += 1
                    continue
                seen.add(key)
                cleaned_rows.append(cleaned)
                accepted_count += 1

        per_file.append(
            {
                "file": filename,
                "brand": brand,
                "raw_rows": raw_count,
                "accepted_rows": accepted_count,
                "exact_duplicates_removed": duplicate_count,
                "rejected_rows": sum(file_rejections.values()),
                "rejection_reasons": dict(sorted(file_rejections.items())),
            }
        )

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    summary = {
        "input_directory": INPUT_ROOT.relative_to(PROJECT_ROOT).as_posix(),
        "output_file": OUTPUT_CSV.relative_to(PROJECT_ROOT).as_posix(),
        "included_files": list(CORE_FILES),
        "excluded_auxiliary_files": [
            "cclass.csv",
            "focus.csv",
            "unclean cclass.csv",
            "unclean focus.csv",
        ],
        "raw_rows": sum(item["raw_rows"] for item in per_file),
        "cleaned_rows": len(cleaned_rows),
        "exact_duplicates_removed": sum(item["exact_duplicates_removed"] for item in per_file),
        "rejected_rows": sum(rejected_reasons.values()),
        "rejection_reasons": dict(sorted(rejected_reasons.items())),
        "engine_size_zero_converted_to_missing": sum(
            int(row["engine_size_missing"]) for row in cleaned_rows
        ),
        "output_columns": OUTPUT_COLUMNS,
        "per_file": per_file,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    summary = preprocess()
    print(
        f"Cleaned {summary['raw_rows']:,} raw rows into "
        f"{summary['cleaned_rows']:,} rows."
    )
    print(
        f"Removed {summary['exact_duplicates_removed']:,} duplicates and "
        f"rejected {summary['rejected_rows']:,} invalid rows."
    )
    print(f"Wrote {OUTPUT_CSV}")
    print(f"Wrote {SUMMARY_JSON}")


if __name__ == "__main__":
    main()
