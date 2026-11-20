import unittest
from itertools import combinations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor

from src.uk_modeling import CATEGORIES, DATA_PATH, NUMBERS, load_splits, pipeline_for, split_listings


def sample_listings():
    return pd.DataFrame({
        "brand": ["Ford"] * 16,
        "model": ["Fiesta"] * 16,
        "transmission": ["Manual"] * 16,
        "fuel_type": ["Petrol"] * 16,
        "year": [2018] * 16,
        "mileage": [20_000 + 1_000 * i for i in range(16)],
        "engine_size": [np.nan, 1.6, 1.2, 1.4] * 4,
        "tax": [150] * 16,
        "mpg": [50.0] * 16,
        "price": [15_000 - 250 * i for i in range(16)],
    })


class SplitListingsTests(unittest.TestCase):
    def test_groups_equal_profiles_with_different_prices_and_missing_values(self):
        listings = sample_listings()
        copies = listings.assign(price=listings.price + 500)
        combined = pd.concat([listings, copies], ignore_index=True)

        partitions = split_listings(combined)
        self.assertTrue(all(len(part) > 0 for part in partitions))
        self.assertCountEqual(pd.concat(partitions).index, combined.index)
        for part in partitions:
            self.assertTrue(part.groupby("mileage").size().eq(2).all())

    def test_same_input_produces_same_partitions(self):
        listings = sample_listings()
        for first, second in zip(split_listings(listings), split_listings(listings)):
            pd.testing.assert_frame_equal(first, second)

    def test_repository_splits_use_all_rows_and_share_no_profiles(self):
        listings = pd.read_csv(DATA_PATH)
        partitions = load_splits()
        pd.testing.assert_frame_equal(pd.concat(partitions).sort_index(), listings)

        profiles = [
            set(rows[CATEGORIES + NUMBERS].itertuples(index=False, name=None))
            for rows in (part.fillna({"engine_size": -1}) for part in partitions)
        ]
        for first, second in combinations(profiles, 2):
            self.assertTrue(first.isdisjoint(second))


class BaselinePipelineTests(unittest.TestCase):
    def test_all_baselines_predict_unseen_categories_and_missing_engine_size(self):
        training = sample_listings()
        car = training.iloc[[0]].drop(columns="price").assign(brand="Unknown", model="Unknown")
        regressors = [
            LinearRegression(),
            DecisionTreeRegressor(random_state=42),
            RandomForestRegressor(n_estimators=2, random_state=42),
        ]

        for regressor in regressors:
            with self.subTest(regressor=type(regressor).__name__):
                model = pipeline_for(regressor).fit(training, training.price)
                predictions = model.predict(car)
                self.assertEqual(predictions.shape, (1,))
                self.assertTrue(np.isfinite(predictions).all())

    def test_preprocessor_excludes_price_and_adds_missing_engine_indicator(self):
        training = sample_listings()
        model = pipeline_for(LinearRegression()).fit(training, training.price)
        names = model.steps[0][1].get_feature_names_out()
        self.assertFalse(any("price" in name for name in names))
        self.assertIn("number__missingindicator_engine_size", names)


if __name__ == "__main__":
    unittest.main()
