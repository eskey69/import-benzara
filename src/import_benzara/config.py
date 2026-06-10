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
