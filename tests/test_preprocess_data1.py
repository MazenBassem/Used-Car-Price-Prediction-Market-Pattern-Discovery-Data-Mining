import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from preprocess_data1 import RejectedRow, normalize_row  # noqa: E402


class NormalizeData1RowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.row = {
            "model": " Fiesta ",
            "year": "2018",
            "price": "12000",
            "transmission": " Manual ",
            "mileage": "25000",
            "fuelType": " Petrol ",
            "tax": "145",
            "mpg": "55.4",
            "engineSize": "1.0",
        }

    def test_normalizes_headers_values_and_brand(self) -> None:
        cleaned = normalize_row(self.row, "Ford")
        self.assertEqual(cleaned["brand"], "Ford")
        self.assertEqual(cleaned["model"], "Fiesta")
        self.assertEqual(cleaned["fuel_type"], "Petrol")
        self.assertEqual(cleaned["engine_size"], 1.0)
        self.assertEqual(cleaned["engine_size_missing"], 0)

    def test_accepts_hyundai_tax_header(self) -> None:
        self.row["tax(£)"] = self.row.pop("tax")
        cleaned = normalize_row(self.row, "Hyundai")
        self.assertEqual(cleaned["tax"], 145.0)

    def test_zero_engine_size_becomes_missing_with_flag(self) -> None:
        self.row["engineSize"] = "0"
        cleaned = normalize_row(self.row, "Ford")
        self.assertEqual(cleaned["engine_size"], "")
        self.assertEqual(cleaned["engine_size_missing"], 1)

    def test_rejects_future_year(self) -> None:
        self.row["year"] = "2060"
        with self.assertRaisesRegex(RejectedRow, "year_outside_1970_2020"):
            normalize_row(self.row, "Ford")


if __name__ == "__main__":
    unittest.main()
