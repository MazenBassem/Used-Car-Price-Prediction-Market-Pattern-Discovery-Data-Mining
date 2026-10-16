import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from preprocess_data2 import RejectedRow, normalize_row, optional_text  # noqa: E402


class NormalizeData2RowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.row = {
            "brand": " Ford ",
            "model": " F-150 XLT ",
            "model_year": "2020",
            "milage": "51,000 mi.",
            "fuel_type": " Gasoline ",
            "engine": "3.5L V6",
            "transmission": "10-Speed A/T",
            "ext_col": "Black",
            "int_col": "Gray",
            "accident": "None reported",
            "clean_title": "Yes",
            "price": "$35,500",
        }

    def test_parses_formatted_numeric_values_and_renames_fields(self) -> None:
        cleaned = normalize_row(self.row)
        self.assertEqual(cleaned["brand"], "Ford")
        self.assertEqual(cleaned["mileage"], 51_000)
        self.assertEqual(cleaned["price"], 35_500)
        self.assertEqual(cleaned["exterior_color"], "Black")
        self.assertEqual(cleaned["interior_color"], "Gray")

    def test_normalizes_dash_and_blank_to_missing(self) -> None:
        self.assertEqual(optional_text("–"), "")
        self.assertEqual(optional_text("  "), "")

    def test_preserves_unknown_accident_and_title_as_missing(self) -> None:
        self.row["accident"] = ""
        self.row["clean_title"] = ""
        cleaned = normalize_row(self.row)
        self.assertEqual(cleaned["accident"], "")
        self.assertEqual(cleaned["clean_title"], "")

    def test_rejects_unparseable_price(self) -> None:
        self.row["price"] = "price unavailable"
        with self.assertRaisesRegex(RejectedRow, "invalid_price"):
            normalize_row(self.row)


if __name__ == "__main__":
    unittest.main()
