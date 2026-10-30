import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from preprocess_data3 import RejectedRow, normalize_row  # noqa: E402


class NormalizeData3RowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.row = {
            "car_ID": "1",
            "symboling": "3",
            "CarName": "maxda rx3",
            "fueltype": "gas",
            "aspiration": "std",
            "doornumber": "two",
            "carbody": "convertible",
            "drivewheel": "rwd",
            "enginelocation": "front",
            "wheelbase": "88.6",
            "carlength": "168.8",
            "carwidth": "64.1",
            "carheight": "48.8",
            "curbweight": "2548",
            "enginetype": "dohc",
            "cylindernumber": "four",
            "enginesize": "130",
            "fuelsystem": "mpfi",
            "boreratio": "3.47",
            "stroke": "2.68",
            "compressionratio": "9",
            "horsepower": "111",
            "peakrpm": "5000",
            "citympg": "21",
            "highwaympg": "27",
            "price": "13495",
        }

    def test_extracts_model_and_normalizes_brand_alias(self) -> None:
        cleaned = normalize_row(self.row)
        self.assertEqual(cleaned["brand"], "mazda")
        self.assertEqual(cleaned["model"], "rx3")
        self.assertEqual(cleaned["price"], 13495)
        self.assertEqual(cleaned["wheelbase"], 88.6)

    def test_normalizes_text_case_and_whitespace(self) -> None:
        self.row["CarName"] = "  Toyota COROLLA  "
        self.row["fueltype"] = " GAS "
        cleaned = normalize_row(self.row)
        self.assertEqual(cleaned["brand"], "toyota")
        self.assertEqual(cleaned["model"], "corolla")
        self.assertEqual(cleaned["fuel_type"], "gas")

    def test_rejects_nonpositive_price(self) -> None:
        self.row["price"] = "0"
        with self.assertRaisesRegex(RejectedRow, "nonpositive_price"):
            normalize_row(self.row)


if __name__ == "__main__":
    unittest.main()
