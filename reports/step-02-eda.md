# Step 2 Report: Exploratory Data Analysis for Data 3

## Scope

Step 2 examines the cleaned Car Price Assignment dataset (Data 3). The
analysis is descriptive only: it summarizes the dataset, checks quality,
visualizes distributions, compares vehicle segments, and studies associations
with price.

This step does not include train/test splitting, feature encoding, scaling,
regression, prediction, or clustering. The two hundred and one observations
remain in one table so that the exploratory results describe the complete
cleaned dataset.

## Dataset overview

### Input and output

- Raw input: `data/raw_data/CarPrice_Assignment.csv`
- Cleaned input used for EDA: `data/processed/data3_cleaned.csv`
- Raw rows: 205
- Cleaned rows: 201
- Columns: 27
- Price unit: dataset price units

The preprocessing step rejected four rows because their price values were
invalid. No exact duplicate rows remain in the cleaned table, and every
output column has zero missing values.

### Dataset fields

| Field group | Columns |
|---|---|
| Identification | `car_id`, `brand`, `model` |
| Vehicle description | `symboling`, `doors`, `body_style`, `drive_wheel`, `engine_location` |
| Fuel and engine | `fuel_type`, `aspiration`, `engine_type`, `cylinders`, `engine_size`, `fuel_system` |
| Dimensions | `wheelbase`, `car_length`, `car_width`, `car_height`, `curb_weight` |
| Engine measurements | `bore_ratio`, `stroke`, `compression_ratio`, `horsepower`, `peak_rpm` |
| Efficiency and target | `city_mpg`, `highway_mpg`, `price` |

## Data quality checks

The EDA notebook displays the first rows, data types, missing-value counts,
unique-value counts, duplicate count, and descriptive statistics. The
resulting checks are:

| Check | Result |
|---|---:|
| Rows | 201 |
| Columns | 27 |
| Duplicate rows | 0 |
| Columns with missing values | 0 |
| Minimum price | 5,118 |
| Maximum price | 45,400 |

The cleaned table is therefore suitable for descriptive plots without an
additional imputation step.

## Univariate analysis

### Numerical variables

| Variable | Minimum | Median | Mean | Maximum |
|---|---:|---:|---:|---:|
| `price` | 5,118 | 10,295 | 13,207.13 | 45,400 |
| `horsepower` | 48 | 95 | 103.26 | 262 |
| `engine_size` | 61 | 120 | 126.88 | 326 |
| `curb_weight` | 1,488 | 2,414 | 2,555.67 | 4,066 |
| `city_mpg` | 13 | 24 | 25.18 | 49 |
| `highway_mpg` | 16 | 30 | 30.69 | 54 |
| `wheelbase` | 86.6 | 97.0 | 98.80 | 120.9 |
| `car_width` | 60.3 | 65.5 | 65.89 | 72.0 |

The notebook plots histograms with density curves for the numerical fields.
The difference between the mean and median price indicates a right-skewed
price distribution, so medians are reported alongside means in the segment
comparisons.

### Categorical variables

| Variable | Most common category | Count |
|---|---|---:|
| `fuel_type` | gas | 181 |
| `aspiration` | std | 165 |
| `doors` | four | 114 |
| `body_style` | sedan | 94 |
| `drive_wheel` | fwd | 118 |
| `engine_location` | front | 198 |
| `engine_type` | ohc | 145 |
| `cylinders` | four | 157 |
| `fuel_system` | mpfi | 92 |

The categorical plots show that the sample is not evenly balanced across
vehicle types. In particular, gas, front-engine, four-cylinder, and standard
aspiration vehicles dominate the dataset.

## Price analysis

The notebook uses a histogram, box plot, and log-transformed histogram to
inspect price spread and potential outliers. The five highest-priced
observations are:

| Brand | Model | Price |
|---|---|---:|
| Buick | regal sport coupe (turbo) | 45,400 |
| BMW | x5 | 41,315 |
| Buick | century special | 40,960 |
| Porsche | boxter | 37,028 |
| BMW | x3 | 36,880 |

The five lowest-priced observations are:

| Brand | Model | Price |
|---|---|---:|
| Subaru | unknown | 5,118 |
| Chevrolet | impala | 5,151 |
| Mazda | rx3 | 5,195 |
| Toyota | corona mark ii | 5,348 |
| Mitsubishi | mirage | 5,389 |

These observations are reported for investigation rather than automatic
removal. A high or low price may represent a real vehicle segment.

## Segment comparisons

The notebook compares price distributions by body style, fuel type, brand,
drive wheel, and aspiration. The following tables use median price because it
is less sensitive to extreme observations.

### Body style

| Body style | Cars | Median price | Mean price |
|---|---:|---:|---:|
| hardtop | 8 | 28,176 | 22,208.50 |
| convertible | 6 | 17,669 | 21,890.50 |
| wagon | 25 | 11,694 | 12,371.96 |
| sedan | 94 | 11,259 | 14,459.76 |
| hatchback | 68 | 8,845 | 9,957.44 |

Hardtops have the highest median price, while hatchbacks have the lowest.
The hardtop and convertible groups are small, so their medians should be
interpreted cautiously.

### Fuel type and drivetrain

| Group | Category | Cars | Median price |
|---|---|---:|---:|
| Fuel type | diesel | 20 | 13,860 |
| Fuel type | gas | 181 | 9,989 |
| Drive wheel | rwd | 75 | 16,900 |
| Drive wheel | 4wd | 8 | 9,233 |
| Drive wheel | fwd | 118 | 8,195 |
| Aspiration | turbo | 36 | 16,503 |
| Aspiration | std | 165 | 9,538 |

Diesel, rear-wheel drive, and turbo vehicles have higher median prices in
this sample. These are associations, not causal conclusions, and the group
sizes are uneven.

## Numerical relationships with price

The correlation heatmap and price correlation table identify the strongest
linear associations among the examined numerical variables:

| Variable | Correlation with price |
|---|---:|
| `engine_size` | 0.872 |
| `curb_weight` | 0.834 |
| `horsepower` | 0.811 |
| `car_width` | 0.751 |
| `wheelbase` | 0.585 |
| `compression_ratio` | 0.071 |
| `city_mpg` | -0.687 |
| `highway_mpg` | -0.705 |

Engine size, curb weight, and horsepower show strong positive associations
with price. City and highway fuel economy show strong negative associations.
Correlation does not prove causation and may reflect relationships among the
vehicle measurements themselves.

The notebook also uses scatter plots for price against horsepower, engine
size, and curb weight, colored by relevant categorical variables. These plots
help assess whether the relationships are approximately monotonic and whether
different vehicle segments occupy different price ranges.

## Main EDA findings

1. The cleaned Data 3 table contains 201 complete, non-duplicate records.
2. Prices are right-skewed, with a mean above the median and a small number of
   high-priced observations.
3. The dataset is dominated by gas-powered, front-engine, four-cylinder,
   standard-aspiration vehicles.
4. Hardtops, turbo vehicles, and rear-wheel-drive vehicles have the highest
   median prices among the reported groups, although some groups are small.
5. Engine size, curb weight, and horsepower have the strongest positive
   numerical associations with price.
6. Fuel economy has a negative association with price in this dataset.
7. The findings support later feature-engineering and modeling hypotheses but
   do not establish causal effects or guarantee predictive performance.

## Reproducibility

- `src/preprocess_data3.py` rebuilds the cleaned Data 3 table.
- `notebooks/EDA_Step.ipynb` contains the complete EDA workflow and charts.
- `outputs/step-01/data3_preprocessing_summary.json` records the preprocessing
  row counts, rejected rows, normalized aliases, and missing-value checks.
- `tests/test_preprocess_data3.py` tests the Data 3 cleaning rules.

## Step 2 status

Exploratory analysis is complete for Data 3. Model training, train/test
splitting, preprocessing pipelines for modeling, and clustering remain
separate future steps.
