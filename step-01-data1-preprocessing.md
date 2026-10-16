# Step 1 Report: Data 1 Audit and Preprocessing

## Outcome

The nine core manufacturer files from the 100,000 UK Used Car Dataset were combined into one reproducible cleaned dataset:

- Output: `data/processed/data1_cleaned.csv`
- Raw core rows: 99,187
- Cleaned rows: 97,711
- Exact duplicates removed: 1,475
- Invalid rows removed: 1
- Final columns: 11

The raw files were not changed. Data 2 was deliberately left untouched so each dataset can be processed according to its own schema and market.

## Why Data 1 Was Chosen First

Data 1 is the primary, approximately 100,000-row UK dataset and has a mostly consistent structured schema. It is the better starting point for building the project's cleaning, exploratory analysis, and modeling workflow. Data 2 has only 4,009 rows and contains more complex free-text engine and transmission fields, currency-formatted prices, mileage units, missing values, and placeholder symbols; it will receive a separate preprocessing pipeline later.

The referenced [Kaggle car-price notebook](https://www.kaggle.com/code/zabihullah18/car-price-prediction) is useful as a high-level workflow example. Its input contains different vehicle specification variables, so its cleaning rules should not be copied directly into this project.

## Input Selection

The following nine files form the core dataset and were included:

| File | Standardized brand | Raw rows | Cleaned rows | Duplicates removed | Invalid rows removed |
|---|---:|---:|---:|---:|---:|
| `audi.csv` | Audi | 10,668 | 10,565 | 103 | 0 |
| `bmw.csv` | BMW | 10,781 | 10,664 | 117 | 0 |
| `ford.csv` | Ford | 17,965 | 17,810 | 154 | 1 |
| `hyundi.csv` | Hyundai | 4,860 | 4,774 | 86 | 0 |
| `merc.csv` | Mercedes-Benz | 13,119 | 12,860 | 259 | 0 |
| `skoda.csv` | Skoda | 6,267 | 6,188 | 79 | 0 |
| `toyota.csv` | Toyota | 6,738 | 6,699 | 39 | 0 |
| `vauxhall.csv` | Vauxhall | 13,632 | 13,258 | 374 | 0 |
| `vw.csv` | Volkswagen | 15,157 | 14,893 | 264 | 0 |
| **Total** |  | **99,187** | **97,711** | **1,475** | **1** |

Four auxiliary files were excluded from the combined modeling table:

- `focus.csv`: 5,454 cleaned rows; 4,670 rows (85.63%) match `ford.csv` on the seven common columns.
- `cclass.csv`: 3,899 cleaned rows; 3,634 rows (93.20%) match `merc.csv` on the seven common columns.
- `unclean focus.csv` and `unclean cclass.csv`: retained only as raw/reference versions of the two auxiliary files.

Combining these files with the nine core files would substantially double-count Focus and C-Class observations.

## Cleaning Rules Applied

1. Added `brand` from the source filename and standardized abbreviated or misspelled names such as `hyundi`, `merc`, and `vw`.
2. Standardized headers:
   - `fuelType` to `fuel_type`
   - `engineSize` to `engine_size`
   - Hyundai's `tax(£)` to `tax`
3. Trimmed leading and trailing whitespace. This was necessary because nearly every raw `model` value begins with whitespace.
4. Converted numeric fields to validated numeric representations.
5. Removed exact duplicate records after normalization and after adding the brand.
6. Removed one Ford Fiesta record with model year 2060. All other Data 1 records end at model year 2020, so the value cannot be defended without guessing its intended year.
7. Converted `engine_size = 0` to missing because zero is not a usable physical engine displacement. Added `engine_size_missing` as an explicit indicator. After duplicate removal, 268 rows are affected.
8. Preserved zero road tax, very low MPG values, high prices, old vehicles, and other extreme observations. These may be legitimate or influential and require exploratory analysis before any further treatment.

## Cleaned Schema

| Column | Role | Notes |
|---|---|---|
| `brand` | Categorical feature | Derived from source file |
| `model` | Categorical feature | Whitespace trimmed |
| `year` | Numeric feature | Validated to 1970–2020 |
| `price` | Regression target | Positive GBP value |
| `transmission` | Categorical feature | Whitespace trimmed |
| `mileage` | Numeric feature | Non-negative miles |
| `fuel_type` | Categorical feature | Header standardized |
| `tax` | Numeric feature | Header standardized; zero retained |
| `mpg` | Numeric feature | Extreme values retained for EDA |
| `engine_size` | Numeric feature | Zero converted to missing |
| `engine_size_missing` | Binary feature | 1 when raw engine size was zero |

## Reproducibility

- `src/audit_datasets.py` profiles all raw CSV files and writes `outputs/step-01/dataset_audit.json`.
- `src/preprocess_data1.py` rebuilds the cleaned Data 1 output from the raw files.
- `outputs/step-01/data1_preprocessing_summary.json` records row-level outcomes for every source file.
- `tests/test_preprocess_data1.py` checks header normalization, whitespace cleaning, missing-engine handling, and invalid-year rejection.

## Verification Results

- Four preprocessing unit tests passed.
- Both Python scripts compiled successfully.
- The cleaned output contains exactly 97,711 data rows and the expected 11 columns.
- No exact duplicate groups remain.
- No model years greater than 2020 remain.
- Exactly 268 rows have both a missing `engine_size` and `engine_size_missing = 1`.
- Re-running preprocessing produced the same SHA-256 hash, confirming deterministic output.

## Next Step

Perform exploratory data analysis on the cleaned Data 1 table. This should examine target skew, numeric distributions, price relationships, category frequencies, suspicious MPG and price extremes, and differences across brands. Decisions about outliers, transformations, rare categories, and train/test preprocessing should be made only after that evidence is available.

