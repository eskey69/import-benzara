from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    inventory_csv: Path
    catalog_xlsx: Path
    output_csv: Path
    summary_json: Path
    inventory_only_csv: Path
    catalog_only_csv: Path
    inventory_delimiter: str | None = None
    output_delimiter: str = ";"
    quantity_column: str = "Qty"
    sku_column: str = "SKU"
    catalog_inventory_qty_column: str = "Inventory Qty"
    sync_catalog_inventory_qty: bool = True
    min_qty: int | None = None


@dataclass(slots=True)
class StockFeedConfig:
    inventory_csv: Path
    catalog_xlsx: Path
    output_xml: Path
    summary_json: Path
    inventory_only_csv: Path
    catalog_only_csv: Path
    inventory_delimiter: str | None = None
    sku_column: str = "SKU"
    quantity_column: str = "Qty"
    title_column: str = "Title"
    minimum_stock_threshold: int = 10


@dataclass(slots=True)
class AppPaths:
    data_root: Path
    uploads_root: Path
    uploads_catalog: Path
    uploads_inventory: Path
    generated_root: Path
    generated_runs: Path
    generated_latest: Path


@dataclass(slots=True)
class WebAppConfig:
    data_root: Path
    secret_key: str
    minimum_stock_threshold: int = 10
    admin_username: str | None = None
    admin_password: str | None = None
