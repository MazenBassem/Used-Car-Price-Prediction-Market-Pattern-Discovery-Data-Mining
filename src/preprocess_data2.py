"""Basic cleaning for the Used Car Price Prediction dataset in data2."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "data2" / "used_cars.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "data2_cleaned.csv"
SUMMARY_PATH = PROJECT_ROOT / "outputs" / "step-01" / "data2_preprocessing_summary.json"

PLACEHOLDERS = {"-", "–", "—", "n/a", "na", "null", "unknown", "not available"}
MILEAGE_PATTERN = re.compile(r"^([\d,]+)\s*mi\.?$", flags=re.IGNORECASE)
PRICE_PATTERN = re.compile(r"^\$?([\d,]+)$")
MIN_MODEL_YEAR = 1886
MAX_MODEL_YEAR = 2026

OUTPUT_COLUMNS = [
    "brand",
    "model",
    "model_year",
    "mileage",
    "fuel_type",
    "engine",
    "transmission",
    "exterior_color",
    "interior_color",
    "accident",
    "clean_title",
    "price",
]


class RejectedRow(ValueError):
    """Raised when a required value cannot be cleaned safely."""


def optional_text(value: str | None) -> str:
    """Trim text and normalize known missing-value placeholders to blank."""
    cleaned = (value or "").strip()
    return "" if cleaned.casefold() in PLACEHOLDERS else cleaned


def required_text(value: str | None, field: str) -> str:
    cleaned = optional_text(value)
    if not cleaned:
        raise RejectedRow(f"missing_{field}")
    return cleaned


def parse_integer(value: str | None, pattern: re.Pattern[str], field: str) -> int:
    cleaned = required_text(value, field)
    match = pattern.fullmatch(cleaned)
    if not match:
        raise RejectedRow(f"invalid_{field}")
    return int(match.group(1).replace(",", ""))


def normalize_row(raw: dict[str, str]) -> dict[str, Any]:
    model_year_text = required_text(raw.get("model_year"), "model_year")
    try:
        model_year = int(model_year_text)
    except ValueError as error:
        raise RejectedRow("invalid_model_year") from error
    if model_year < MIN_MODEL_YEAR or model_year > MAX_MODEL_YEAR:
        raise RejectedRow("model_year_out_of_range")

    mileage = parse_integer(raw.get("milage"), MILEAGE_PATTERN, "mileage")
    if mileage < 0:
        raise RejectedRow("negative_mileage")

    price = parse_integer(raw.get("price"), PRICE_PATTERN, "price")
    if price <= 0:
        raise RejectedRow("nonpositive_price")

    return {
        "brand": required_text(raw.get("brand"), "brand"),
        "model": required_text(raw.get("model"), "model"),
        "model_year": model_year,
        "mileage": mileage,
        "fuel_type": optional_text(raw.get("fuel_type")),
        "engine": optional_text(raw.get("engine")),
        "transmission": optional_text(raw.get("transmission")),
        "exterior_color": optional_text(raw.get("ext_col")),
        "interior_color": optional_text(raw.get("int_col")),
        "accident": optional_text(raw.get("accident")),
        "clean_title": optional_text(raw.get("clean_title")),
        "price": price,
    }


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
        reader = csv.DictReader(handle)
        for raw in reader:
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
    numeric_ranges = {
        column: {
            "minimum": min(int(row[column]) for row in cleaned_rows),
            "maximum": max(int(row[column]) for row in cleaned_rows),
        }
        for column in ("model_year", "mileage", "price")
    }
    summary = {
        "input_file": INPUT_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "output_file": OUTPUT_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "raw_rows": raw_rows,
        "cleaned_rows": len(cleaned_rows),
        "exact_duplicates_removed_after_normalization": duplicates_removed,
        "rejected_rows": sum(rejection_reasons.values()),
        "rejection_reasons": dict(sorted(rejection_reasons.items())),
        "output_columns": OUTPUT_COLUMNS,
        "missing_counts_after_normalization": missing_counts,
        "numeric_ranges": numeric_ranges,
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
