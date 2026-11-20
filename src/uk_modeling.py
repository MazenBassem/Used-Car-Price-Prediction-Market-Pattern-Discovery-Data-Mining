"""Shared data preparation for the UK used-car modeling notebooks."""

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler


CATEGORIES = ["brand", "model", "transmission", "fuel_type"]
NUMBERS = ["year", "mileage", "engine_size", "tax", "mpg"]
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "data1_cleaned.csv"


def _split_profiles(frame):
    profiles = pd.util.hash_pandas_object(frame[CATEGORIES + NUMBERS], index=False)
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    fit_rows, held_out_rows = next(splitter.split(frame, groups=profiles))
    return frame.iloc[fit_rows], frame.iloc[held_out_rows]


def split_listings(frame):
    """Return training, validation, and testing rows without shared profiles."""
    development, testing = _split_profiles(frame)
    training, validation = _split_profiles(development)
    return training, validation, testing


def load_splits():
    return split_listings(pd.read_csv(DATA_PATH))


def pipeline_for(regressor):
    if isinstance(regressor, LinearRegression):
        encoder = OneHotEncoder(handle_unknown="ignore")
    else:
        encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)

    preprocessor = ColumnTransformer([
        ("category", make_pipeline(SimpleImputer(strategy="most_frequent"), encoder), CATEGORIES),
        ("number", make_pipeline(SimpleImputer(strategy="median", add_indicator=True),
                                 StandardScaler()), NUMBERS),
    ])
    return make_pipeline(preprocessor, regressor)
