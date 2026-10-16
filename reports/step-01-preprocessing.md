# Step 1 Report: Basic Preprocessing for Data 1 and Data 2

## Scope

Step 1 covers basic preprocessing only. The two Kaggle datasets were cleaned separately because they describe different markets and use different schemas. They were not merged.

This step includes file selection, column-name standardization, whitespace cleaning, numeric conversion, duplicate handling, invalid-value handling, and missing-value normalization. It does not include charts, exploratory analysis, train/test splitting, encoding, scaling, feature selection, modeling, or clustering.

## Data 1: 100,000 UK Used Car Dataset

### Input selection

Nine broad manufacturer files were selected as the core Data 1 table:

| File | Standardized brand | Raw rows | Cleaned rows | Duplicates removed | Invalid rows removed |
|---|---|---:|---:|---:|---:|
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

The following files were excluded from the core table:

- `focus.csv`: 85.63% of its rows match `ford.csv` on their shared fields.
- `cclass.csv`: 93.20% of its rows match `merc.csv` on their shared fields.
- `unclean focus.csv` and `unclean cclass.csv`: retained as raw reference files only.

Including these auxiliary files would substantially double-count Focus and C-Class records.

### Cleaning performed

1. Combined the nine core files.
2. Added `brand` from each source filename.
3. Standardized `hyundi` to Hyundai, `merc` to Mercedes-Benz, and `vw` to Volkswagen.
4. Renamed `fuelType` to `fuel_type`, `engineSize` to `engine_size`, and Hyundai's `tax(£)` to `tax`.
5. Removed leading and trailing whitespace from text values.
6. Converted numeric fields to validated numeric formats.
7. Removed 1,475 exact duplicate records.
8. Removed one Ford Fiesta record with the impossible model year 2060 rather than guessing its intended year.
9. Converted zero engine sizes to missing values and added `engine_size_missing`. After duplicate removal, 268 rows are affected.
10. Preserved defensible extreme values such as high prices, high mileage, zero tax, and unusual MPG for later analysis.

### Data 1 result

- Output: `data/processed/data1_cleaned.csv`
- Rows: 97,711
- Columns: 11
- Duplicate rows remaining: 0
- Price unit: GBP

## Data 2: Used Car Price Prediction Dataset

### Input

- Source: `data/raw/data2/used_cars.csv`
- Raw rows: 4,009
- Raw columns: 12

### Cleaning performed

1. Trimmed whitespace from text fields.
2. Corrected the misspelled `milage` header to `mileage`.
3. Renamed `ext_col` to `exterior_color` and `int_col` to `interior_color`.
4. Converted formatted mileage such as `51,000 mi.` to integer miles such as `51000`.
5. Converted formatted prices such as `$10,300` to integer USD values such as `10300`.
6. Converted en-dash placeholders in fuel type, engine, transmission, and colors to missing values.
7. Preserved blank accident values as missing rather than assuming that no accident occurred.
8. Preserved blank clean-title values as missing rather than interpreting them as `No`.
9. Checked for exact duplicates after normalization; none were found.
10. Validated model year, mileage, and price. All 4,009 rows passed.
11. Preserved high prices and high mileage because the values remain possible and require later analysis before removal.

### Missing values after normalization

| Column | Missing rows |
|---|---:|
| `fuel_type` | 215 |
| `engine` | 45 |
| `transmission` | 4 |
| `exterior_color` | 15 |
| `interior_color` | 133 |
| `accident` | 113 |
| `clean_title` | 596 |

Brand, model, model year, mileage, and price have no missing values. Missing fields were not imputed during basic preprocessing.

### Validated numeric ranges

| Column | Minimum | Maximum |
|---|---:|---:|
| Model year | 1974 | 2024 |
| Mileage | 100 miles | 405,000 miles |
| Price | $2,000 | $2,954,083 |

### Data 2 result

- Output: `data/processed/data2_cleaned.csv`
- Rows: 4,009
- Columns: 12
- Duplicate rows remaining: 0
- Rejected rows: 0
- Price unit: USD

## Reproducibility

- `src/preprocess_data1.py` rebuilds the cleaned Data 1 table.
- `src/preprocess_data2.py` rebuilds the cleaned Data 2 table.
- `outputs/step-01/data1_preprocessing_summary.json` records Data 1 cleaning results.
- `outputs/step-01/data2_preprocessing_summary.json` records Data 2 cleaning results.
- `tests/test_preprocess_data1.py` tests Data 1 cleaning rules.
- `tests/test_preprocess_data2.py` tests Data 2 cleaning rules.

## Step 1 Status

Basic preprocessing is complete for both Data 1 and Data 2. Later tasks such as exploratory charts, imputation strategies, feature engineering, encoding, scaling, train/test splitting, regression, and clustering are outside Step 1.

