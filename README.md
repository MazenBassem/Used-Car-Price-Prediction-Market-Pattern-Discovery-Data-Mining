# Used Car Price Data Mining Project

This project studies three used-car datasets with different markets and schemas. The preprocessing scripts clean each dataset separately. The Data 3 notebook explores pricing patterns, and the Data 1 notebooks compare models for historical UK listing prices in pounds.

## Data

| Dataset | Where to put raw files | Cleaned file |
| --- | --- | --- |
| Data 1 · [100,000 UK Used Car Dataset](https://www.kaggle.com/datasets/adityadesai13/used-car-dataset-ford-and-mercedes) | `data/raw/data1/` | `data/processed/data1_cleaned.csv` |
| Data 2 · [Used Car Price Prediction Dataset](https://www.kaggle.com/datasets/taeefnajib/used-car-price-prediction-dataset) | `data/raw/data2/used_cars.csv` | `data/processed/data2_cleaned.csv` |
| Data 3 · Car Price Assignment | `data/raw_data/CarPrice_Assignment.csv` (included) | `data/processed/data3_cleaned.csv` |

The cleaned CSVs are included in the repository. The original Data 1 and Data 2 downloads are only needed to rerun preprocessing.

## Setup

From the repository root, create a Python 3.12 environment and install the dependencies.

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, replace the first two commands with `py -3.12 -m venv .venv` and `.\.venv\Scripts\Activate.ps1`.

## Explore and train

Run `python -m jupyterlab` from the repository root and use **Run All** in any notebook.

| Notebook | Purpose |
| --- | --- |
| [car-price-eda.ipynb](notebooks/car-price-eda.ipynb) | Explore Data 3. The [EDA report](reports/step-02-eda.md) includes the findings and figures. |
| [uk-price-baseline.ipynb](notebooks/uk-price-baseline.ipynb) | Compare Linear Regression, Decision Tree, and Random Forest on Data 1. |
| [uk-price-catboost.ipynb](notebooks/uk-price-catboost.ipynb) | Compare CatBoost models fitted to price and log price on Data 1. |
| [uk-price-ft-transformer.ipynb](notebooks/uk-price-ft-transformer.ipynb) | Train an FT-Transformer on Data 1. |

Each modeling notebook runs independently. They use the same deterministic split, allocating roughly 64% of listings to training, 16% to validation, and 20% to testing. Identical vehicle profiles stay in the same partition. Validation MAE selects the model or checkpoint, and the held-out set is used for final MAE, RMSE, and R². Training saves model files and logs locally under `outputs/uk-modeling/`.

## Run the tests

```sh
python -m unittest discover -s tests -v
```

The tests cover all three data-cleaning scripts, reproducibility and isolation of the UK data splits, and prediction with missing numeric values or unseen categories.

## Rebuild the cleaned data

The preprocessing scripts use only the Python standard library. Run the script for the dataset you want to rebuild from the repository root.

```sh
python src/preprocess_data1.py
python src/preprocess_data2.py
python src/preprocess_data3.py
```

The [preprocessing report](reports/step-01-preprocessing.md) documents Data 1 and Data 2. The cleaning summaries for all three datasets are in [outputs/step-01](outputs/step-01/).

Future steps include clustering to find groups of similar listings and comparing pricing patterns across datasets.
