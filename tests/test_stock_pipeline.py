from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from openpyxl import Workbook

from import_benzara.config import StockFeedConfig
from import_benzara.stock_pipeline import generate_stock_feed


def write_catalog_xlsx(path: Path, rows: list[dict[str, str]]) -> None:
    workbook = Workbook()
    sheet = workbook.active
    headers = list(rows[0].keys())
    sheet.append(headers)
    for row in rows:
        sheet.append([row.get(header, "") for header in headers])
    workbook.save(path)


class StockPipelineTest(unittest.TestCase):
    def test_generate_stock_feed_exports_full_catalog_and_zeroes_low_stock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            inventory_path = base / "inventory.csv"
            catalog_path = base / "catalog.xlsx"
            output_xml = base / "feed.xml"
            summary_path = base / "feed.summary.json"
            inventory_only_path = base / "feed.inventory-only.csv"
            catalog_only_path = base / "feed.catalog-only.csv"

            inventory_path.write_text("SKU,Qty\nSKU-1,12\nSKU-2,4\nSKU-4,5\n", encoding="utf-8-sig")
            write_catalog_xlsx(
                catalog_path,
                [
                    {"SKU": "SKU-1", "Title": "Chair"},
                    {"SKU": "SKU-2", "Title": "Table"},
                    {"SKU": "SKU-3", "Title": "Lamp"},
                ],
            )

            summary = generate_stock_feed(
                StockFeedConfig(
                    inventory_csv=inventory_path,
                    catalog_xlsx=catalog_path,
                    output_xml=output_xml,
                    summary_json=summary_path,
                    inventory_only_csv=inventory_only_path,
                    catalog_only_csv=catalog_only_path,
                    minimum_stock_threshold=10,
                )
            )

            self.assertEqual(summary.exported_rows, 3)
            self.assertEqual(summary.in_stock_rows, 1)
            self.assertEqual(summary.out_of_stock_rows, 2)
            self.assertEqual(summary.zeroed_below_threshold_rows, 1)
            self.assertEqual(summary.missing_inventory_zeroed_rows, 1)
            self.assertEqual(summary.inventory_only_rows, 1)
            self.assertEqual(summary.catalog_only_rows, 1)

            xml_tree = ET.parse(output_xml)
            products = xml_tree.findall("./products/product")
            self.assertEqual(len(products), 3)

            rows = {product.findtext("sku"): product for product in products}
            self.assertEqual(rows["SKU-1"].findtext("./stock/qty"), "12")
            self.assertEqual(rows["SKU-1"].findtext("./stock/status"), "instock")
            self.assertEqual(rows["SKU-2"].findtext("./stock/qty"), "0")
            self.assertEqual(rows["SKU-2"].findtext("./stock/status"), "outofstock")
            self.assertEqual(rows["SKU-3"].findtext("./stock/qty"), "0")

            summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary_data["stock_threshold"], 10)

            with inventory_only_path.open("r", encoding="utf-8-sig", newline="") as handle:
                inventory_only_rows = list(csv.DictReader(handle, delimiter=";"))
            self.assertEqual(inventory_only_rows[0]["SKU"], "SKU-4")

    def test_conflicting_duplicate_inventory_blocks_feed_generation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            inventory_path = base / "inventory.csv"
            catalog_path = base / "catalog.xlsx"
            output_xml = base / "feed.xml"
            summary_path = base / "feed.summary.json"
            inventory_only_path = base / "feed.inventory-only.csv"
            catalog_only_path = base / "feed.catalog-only.csv"

            inventory_path.write_text("SKU,Qty\nSKU-1,3\nSKU-1,5\n", encoding="utf-8-sig")
            write_catalog_xlsx(catalog_path, [{"SKU": "SKU-1", "Title": "Chair"}])

            with self.assertRaises(ValueError):
                generate_stock_feed(
                    StockFeedConfig(
                        inventory_csv=inventory_path,
                        catalog_xlsx=catalog_path,
                        output_xml=output_xml,
                        summary_json=summary_path,
                        inventory_only_csv=inventory_only_path,
                        catalog_only_csv=catalog_only_path,
                    )
                )


if __name__ == "__main__":
    unittest.main()
