import unittest
from pathlib import Path

import pandas as pd

from horpach_benzara.image_audit import _drop_image_columns, _image_columns, _new_and_existing_products


class ImageAuditTests(unittest.TestCase):
    def test_image_columns_detects_and_orders_columns(self) -> None:
        df = pd.DataFrame(columns=["Image URL 3", "SKU", "Image URL 1", "Image URL 2"])
        self.assertEqual(_image_columns(df), ["Image URL 1", "Image URL 2", "Image URL 3"])

    def test_drop_image_columns_removes_all_image_fields(self) -> None:
        df = pd.DataFrame([{"SKU": "A1", "Image URL 1": "x", "Image URL 2": "y", "Title": "Chair"}])
        result = _drop_image_columns(df)
        self.assertEqual(list(result.columns), ["SKU", "Title"])

    def test_new_and_existing_products_split_by_woo_sku(self) -> None:
        df = pd.DataFrame(
            [
                {"SKU": "A1", "Title": "Existing"},
                {"SKU": "B2", "Title": "New"},
            ]
        )
        new_df, existing_df = _new_and_existing_products(df, {"A1"})
        self.assertEqual(list(new_df["SKU"]), ["B2"])
        self.assertEqual(list(existing_df["SKU"]), ["A1"])


if __name__ == "__main__":
    unittest.main()
