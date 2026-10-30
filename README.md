# Used Car Price Data Mining Project

This project studies two Kaggle used-car datasets separately, then compares their results to identify pricing patterns that generalize across their different markets and schemas.

## Datasets

1. [100,000 UK Used Car Dataset](https://www.kaggle.com/datasets/adityadesai13/used-car-dataset-ford-and-mercedes)
2. [Used Car Price Prediction Dataset](https://www.kaggle.com/datasets/taeefnajib/used-car-price-prediction-dataset)

Place the downloaded, unchanged dataset files in `data/raw/`. Raw data should not be edited in place.

## Objectives

- Clean missing, duplicate, invalid, and inconsistent data.
- Explore how vehicle characteristics relate to price.
- Prepare reproducible features for modeling.
- Compare Linear Regression, Decision Tree, and Random Forest models.
- Evaluate regression performance with MAE, RMSE, and R-squared.
- Use clustering to find groups of cars with similar characteristics.
- Compare conclusions across the two datasets without merging incompatible markets.

## Structure

- `data/raw/`: original dataset files
- `data/processed/`: cleaned and model-ready data
- `notebooks/`: exploratory and presentation notebooks
- `src/`: reusable Python analysis and modeling code
- `models/`: saved fitted models
- `outputs/`: generated figures, tables, and metrics
- `reports/`: one report for each project step

## Planned Steps

1. Basic preprocessing — completed separately for Data 1 and Data 2
2. Exploratory data analysis
3. Feature engineering and model-specific preprocessing
4. Regression modeling and evaluation
5. Clustering and segment interpretation
6. Cross-dataset comparison
7. Final report and reproducible project packaging

## Current Outputs

- `data/processed/data1_cleaned.csv`: cleaned 97,711-row UK used-car table
- `data/processed/data2_cleaned.csv`: cleaned 4,009-row used-car table
- `data/processed/data3_cleaned.csv`: cleaned Car Price Assignment table
- `reports/step-01-preprocessing.md`: basic preprocessing report for both datasets
- `outputs/step-01/dataset_audit.json`: machine-readable audit of all raw CSV files
- `outputs/step-01/data1_preprocessing_summary.json`: Data 1 cleaning summary
- `outputs/step-01/data2_preprocessing_summary.json`: Data 2 cleaning summary
- `outputs/step-01/data3_preprocessing_summary.json`: Data 3 cleaning summary

## Reproduce Step 1

The preprocessing scripts use only the Python standard library. Run:

```powershell
python .\src\preprocess_data1.py
python .\src\preprocess_data2.py
python .\src\preprocess_data3.py
python -m unittest tests.test_preprocess_data1 tests.test_preprocess_data2 tests.test_preprocess_data3 -v
```

`src/used-car-prediction.ipynb` loads the cleaned Data 3 file when it is
available locally or in a Kaggle dataset. It splits the data before fitting
encoding and scaling transformations, so the exploratory model comparison
does not leak information from the test set.
