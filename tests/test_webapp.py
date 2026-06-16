from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from import_benzara.webapp import create_app


def build_catalog_xlsx_bytes(rows: list[dict[str, str]]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    headers = list(rows[0].keys())
    sheet.append(headers)
    for row in rows:
        sheet.append([row.get(header, "") for header in headers])

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


class WebAppTest(unittest.TestCase):
    def test_dashboard_and_healthz_are_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            app = create_app(data_root=Path(tmp_dir) / "data")
            client = app.test_client()

            dashboard = client.get("/")
            self.assertEqual(dashboard.status_code, 200)
            self.assertIn(b"Import Benzara", dashboard.data)

            healthz = client.get("/healthz")
            self.assertEqual(healthz.status_code, 200)
            self.assertEqual(healthz.data, b"ok")

    def test_upload_and_generate_flow_publishes_public_feed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_root = Path(tmp_dir) / "data"
            app = create_app(data_root=data_root)
            client = app.test_client()

            catalog_bytes = build_catalog_xlsx_bytes(
                [
                    {"SKU": "SKU-1", "Title": "Chair"},
                    {"SKU": "SKU-2", "Title": "Table"},
                ]
            )
            inventory_bytes = b"SKU,Qty\nSKU-1,12\nSKU-2,4\n"

            upload_catalog = client.post(
                "/upload/catalog",
                data={"catalog": (io.BytesIO(catalog_bytes), "FTP Benzara MAY (15-05-2026).xlsx")},
                content_type="multipart/form-data",
                follow_redirects=True,
            )
            self.assertEqual(upload_catalog.status_code, 200)

            upload_inventory = client.post(
                "/upload/inventory",
                data={"inventory": (io.BytesIO(inventory_bytes), "Benzara Inventory_19_05_2023.csv")},
                content_type="multipart/form-data",
                follow_redirects=True,
            )
            self.assertEqual(upload_inventory.status_code, 200)

            generated = client.post(
                "/generate",
                data={"minimum_stock_threshold": "10"},
                follow_redirects=True,
            )
            self.assertEqual(generated.status_code, 200)
            self.assertIn(b"Wygenerowano feed XML", generated.data)

            public_feed = client.get("/feed.xml")
            self.assertEqual(public_feed.status_code, 200)
            public_feed_data = public_feed.get_data()
            public_feed.close()
            self.assertIn(b"<sku>SKU-1</sku>", public_feed_data)
            self.assertIn(b"<qty>12</qty>", public_feed_data)
            self.assertIn(b"<sku>SKU-2</sku>", public_feed_data)
            self.assertIn(b"<qty>0</qty>", public_feed_data)

            latest_summary = data_root / "generated" / "latest" / "feed.summary.json"
            self.assertTrue(latest_summary.exists())


if __name__ == "__main__":
    unittest.main()
