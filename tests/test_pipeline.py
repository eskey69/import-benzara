from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from import_benzara.config import AppConfig
from import_benzara.pipeline import generate_feed


class PipelineTest(unittest.TestCase):
    def test_generate_feed_creates_output_and_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            inventory_path = base / "inventory.csv"
            catalog_path = base / "catalog.xlsx"
            output_path = base / "output.csv"
            summary_path = base / "summary.json"
            inventory_only_path = base / "inventory-only.csv"
            catalog_only_path = base / "catalog-only.csv"

            inventory_path.write_text("SKU,Qty\nSKU-1,4\nSKU-3,9\n", encoding="utf-8-sig")

            dataframe = pd.DataFrame(
                [
                    {"SKU": "SKU-1", "Inventory Qty": "10", "Title": "Chair", "Wholesale Price": "100.00"},
                    {"SKU": "SKU-2", "Inventory Qty": "8", "Title": "Table", "Wholesale Price": "250.00"},
                ]
            )
            dataframe.to_excel(catalog_path, index=False)

            config = AppConfig(
                inventory_csv=inventory_path,
                catalog_xlsx=catalog_path,
                output_csv=output_path,
                summary_json=summary_path,
                inventory_only_csv=inventory_only_path,
                catalog_only_csv=catalog_only_path,
                output_delimiter=";",
            )

            summary = generate_feed(config)

            self.assertEqual(summary.matched_rows, 1)
            self.assertEqual(summary.inventory_only_rows, 1)
            self.assertEqual(summary.catalog_only_rows, 1)

            with output_path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle, delimiter=";"))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["SKU"], "SKU-1")
            self.assertEqual(rows[0]["Inventory Qty"], "4")
            self.assertEqual(rows[0]["Qty"], "4")

            with inventory_only_path.open("r", encoding="utf-8-sig", newline="") as handle:
                inventory_only_rows = list(csv.DictReader(handle, delimiter=";"))
            self.assertEqual(inventory_only_rows[0]["SKU"], "SKU-3")

            with catalog_only_path.open("r", encoding="utf-8-sig", newline="") as handle:
                catalog_only_rows = list(csv.DictReader(handle, delimiter=";"))
            self.assertEqual(catalog_only_rows[0]["SKU"], "SKU-2")

            summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary_data["matched_rows"], 1)

    def test_min_qty_does_not_create_false_inventory_only_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            inventory_path = base / "inventory.csv"
            catalog_path = base / "catalog.xlsx"
            output_path = base / "output.csv"
            summary_path = base / "summary.json"
            inventory_only_path = base / "inventory-only.csv"
            catalog_only_path = base / "catalog-only.csv"

            inventory_path.write_text("SKU,Qty\nSKU-1,2\n", encoding="utf-8-sig")
            pd.DataFrame([{"SKU": "SKU-1", "Inventory Qty": "9", "Title": "Lamp"}]).to_excel(catalog_path, index=False)

            config = AppConfig(
                inventory_csv=inventory_path,
                catalog_xlsx=catalog_path,
                output_csv=output_path,
                summary_json=summary_path,
                inventory_only_csv=inventory_only_path,
                catalog_only_csv=catalog_only_path,
                min_qty=5,
            )

            summary = generate_feed(config)
            self.assertEqual(summary.matched_rows, 0)
            self.assertEqual(summary.inventory_only_rows, 0)
            self.assertEqual(summary.skipped_by_min_qty, 1)


if __name__ == "__main__":
    unittest.main()
