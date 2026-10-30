"""Clean the Kaggle Car Price Assignment dataset.

The raw dataset is kept unchanged. This module normalizes column names and
values, extracts the brand and model from ``CarName``, validates numeric
measurements, removes exact duplicates, and writes a model-ready CSV.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "raw_data" / "CarPrice_Assignment.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "data3_cleaned.csv"
SUMMARY_PATH = PROJECT_ROOT / "outputs" / "step-01" / "data3_preprocessing_summary.json"

OUTPUT_COLUMNS = [
    "car_id",
    "symboling",
    "brand",
    "model",
    "fuel_type",
    "aspiration",
    "doors",
    "body_style",
    "drive_wheel",
    "engine_location",
    "wheelbase",
    "car_length",
    "car_width",
    "car_height",
    "curb_weight",
    "engine_type",
    "cylinders",
    "engine_size",
    "fuel_system",
    "bore_ratio",
    "stroke",
    "compression_ratio",
    "horsepower",
    "peak_rpm",
    "city_mpg",
    "highway_mpg",
    "price",
]

BRAND_ALIASES = {
    "maxda": "mazda",
    "mercedes-benz": "mercedes",
    "porcshce": "porsche",
    "toyouta": "toyota",
    "vokswagen": "volkswagen",
}
PLACEHOLDERS = {"", "-", "n/a", "na", "null", "unknown"}
TEXT_FIELDS = {
    "fuel_type": "fueltype",
    "aspiration": "aspiration",
    "doors": "doornumber",
    "body_style": "carbody",
    "drive_wheel": "drivewheel",
    "engine_location": "enginelocation",
    "engine_type": "enginetype",
    "cylinders": "cylindernumber",
    "fuel_system": "fuelsystem",
}
NUMERIC_FIELDS = {
    "car_id": ("car_ID", int, False),
    "symboling": ("symboling", int, False),
    "wheelbase": ("wheelbase", float, True),
    "car_length": ("carlength", float, True),
    "car_width": ("carwidth", float, True),
    "car_height": ("carheight", float, True),
    "curb_weight": ("curbweight", int, True),
    "engine_size": ("enginesize", int, True),
    "bore_ratio": ("boreratio", float, True),
    "stroke": ("stroke", float, True),
    "compression_ratio": ("compressionratio", float, True),
    "horsepower": ("horsepower", int, True),
    "peak_rpm": ("peakrpm", int, True),
    "city_mpg": ("citympg", int, True),
    "highway_mpg": ("highwaympg", int, True),
    "price": ("price", int, True),
}


class RejectedRow(ValueError):
    """Raised when a raw record cannot be cleaned safely."""


def clean_text(value: str | None, field: str, *, required: bool = True) -> str:
    cleaned = (value or "").strip().casefold()
    if cleaned in PLACEHOLDERS:
        if required:
            raise RejectedRow(f"missing_{field}")
        return ""
    return cleaned


def parse_number(value: str | None, field: str, converter: type[int] | type[float]) -> int | float:
    cleaned = clean_text(value, field)
    try:
        number = converter(cleaned)
    except ValueError as error:
        raise RejectedRow(f"invalid_{field}") from error
    if number != number:
        raise RejectedRow(f"invalid_{field}")
    return number


def normalize_brand_and_model(value: str | None) -> tuple[str, str]:
    car_name = clean_text(value, "car_name")
    parts = re.split(r"\s+", car_name, maxsplit=1)
    brand = BRAND_ALIASES.get(parts[0], parts[0])
    model = parts[1] if len(parts) == 2 else "unknown"
    return brand, model


def normalize_row(raw: dict[str, str]) -> dict[str, Any]:
    """Normalize and validate one raw CSV record."""
    brand, model = normalize_brand_and_model(raw.get("CarName"))
    cleaned: dict[str, Any] = {
        "brand": brand,
        "model": model,
    }

    for output, source in TEXT_FIELDS.items():
        cleaned[output] = clean_text(raw.get(source), output)

    for output, (source, converter, must_be_positive) in NUMERIC_FIELDS.items():
        number = parse_number(raw.get(source), output, converter)
        if must_be_positive and number <= 0:
            raise RejectedRow(f"nonpositive_{output}")
        cleaned[output] = number

    if cleaned["car_id"] <= 0:
        raise RejectedRow("nonpositive_car_id")
    return {column: cleaned[column] for column in OUTPUT_COLUMNS}


def row_key(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(row[column]) for column in OUTPUT_COLUMNS)


def preprocess() -> dict[str, Any]:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing required input file: {INPUT_PATH}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)

    raw_rows = 0
    duplicates_removed = 0
    rejection_reasons: Counter[str] = Counter()
    seen: set[tuple[str, ...]] = set()
    cleaned_rows: list[dict[str, Any]] = []

    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        for raw in csv.DictReader(handle):
            raw_rows += 1
            try:
                cleaned = normalize_row(raw)
            except RejectedRow as error:
                rejection_reasons[str(error)] += 1
                continue
            key = row_key(cleaned)
            if key in seen:
                duplicates_removed += 1
                continue
            seen.add(key)
            cleaned_rows.append(cleaned)

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    missing_counts = {
        column: sum(str(row[column]).strip() == "" for row in cleaned_rows)
        for column in OUTPUT_COLUMNS
    }
    summary = {
        "input_file": INPUT_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "output_file": OUTPUT_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "raw_rows": raw_rows,
        "cleaned_rows": len(cleaned_rows),
        "exact_duplicates_removed_after_normalization": duplicates_removed,
        "rejected_rows": sum(rejection_reasons.values()),
        "rejection_reasons": dict(sorted(rejection_reasons.items())),
        "brand_aliases_normalized": BRAND_ALIASES,
        "output_columns": OUTPUT_COLUMNS,
        "missing_counts_after_normalization": missing_counts,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    summary = preprocess()
    print(
        f"Cleaned {summary['raw_rows']:,} raw rows into "
        f"{summary['cleaned_rows']:,} rows."
    )
    print(
        f"Removed {summary['exact_duplicates_removed_after_normalization']:,} duplicates "
        f"and rejected {summary['rejected_rows']:,} invalid rows."
    )
    print(f"Wrote {OUTPUT_PATH}")
    print(f"Wrote {SUMMARY_PATH}")


if __name__ == "__main__":
    main()