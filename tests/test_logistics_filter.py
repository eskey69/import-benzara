import unittest

import pandas as pd

from horpach_benzara.filtering.logistics import split_by_logistics


class LogisticsFilterTests(unittest.TestCase):
    def test_split_by_logistics_separates_allowed_and_removed_rows(self) -> None:
        df = pd.DataFrame(
            [
                {
                    "SKU": "OK-001",
                    "Title": "Small Package Chair",
                    "Inventory Qty": 15,
                    "Product Weight 2": 99,
                    "Product Length 2": 99,
                    "Product Width 2": 99,
                    "Product Height 2": 99,
                    "Ship Weight 1": 18,
                    "Ship Length 1": 30,
                    "Ship Width 1": 18,
                    "Ship Height 1": 12,
                    "Ship Weight 2": 999,
                    "Ship Length 2": 999,
                    "Ship Width 2": 999,
                    "Ship Height 2": 999,
                    "Number Of Boxes": 1,
                    "Ship Type Small Package/LTL": "Small Package",
                },
                {
                    "SKU": "BAD-001",
                    "Title": "Heavy Table",
                    "Inventory Qty": 8,
                    "Ship Weight 1": 35,
                    "Ship Length 1": 50,
                    "Ship Width 1": 18,
                    "Ship Height 1": 12,
                    "Number Of Boxes": 2,
                    "Ship Type Small Package/LTL": "Freight",
                },
            ]
        )

        allowed_df, removed_df = split_by_logistics(df)

        self.assertEqual(list(allowed_df["SKU"]), ["OK-001"])
        self.assertEqual(list(removed_df["SKU"]), ["BAD-001"])
        self.assertEqual(allowed_df.iloc[0]["logistics_status"], "preferred")
        self.assertNotIn("Product Weight 2", allowed_df.columns)
        self.assertNotIn("Ship Weight 2", allowed_df.columns)
        self.assertIn("ship_weight_gt_30", removed_df.iloc[0]["remove_reason"])
        self.assertIn("ship_length_gt_48", removed_df.iloc[0]["remove_reason"])
        self.assertIn("boxes_gt_1", removed_df.iloc[0]["remove_reason"])
        self.assertIn("ship_type_not_small_package", removed_df.iloc[0]["remove_reason"])
        self.assertIn("inventory_lt_10", removed_df.iloc[0]["remove_reason"])


if __name__ == "__main__":
    unittest.main()
