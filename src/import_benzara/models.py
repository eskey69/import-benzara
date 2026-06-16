from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class InventoryIssue:
    row_number: int
    sku: str
    message: str


@dataclass(slots=True)
class InventoryData:
    quantities: dict[str, int]
    row_count: int
    duplicate_skus: list[InventoryIssue]
    invalid_rows: list[InventoryIssue]
    conflicting_duplicate_skus: list[InventoryIssue]


@dataclass(slots=True)
class CatalogRow:
    row_number: int
    values: dict[str, str]


@dataclass(slots=True)
class CatalogData:
    headers: list[str]
    rows: list[CatalogRow]
    sku_header: str
    inventory_qty_header: str | None


@dataclass(slots=True)
class GenerationSummary:
    inventory_rows: int
    catalog_rows: int
    matched_rows: int
    inventory_only_rows: int
    catalog_only_rows: int
    invalid_inventory_rows: int
    duplicate_inventory_skus: int
    blank_catalog_skus: int
    skipped_by_min_qty: int
    output_csv: str
    summary_json: str
    inventory_only_csv: str
    catalog_only_csv: str
    assumptions: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class StockFeedSummary:
    catalog_file: str
    inventory_file: str
    stock_threshold: int
    inventory_rows: int
    catalog_rows: int
    exported_rows: int
    inventory_only_rows: int
    catalog_only_rows: int
    invalid_inventory_rows: int
    duplicate_inventory_rows: int
    conflicting_duplicate_inventory_rows: int
    blank_catalog_skus: int
    in_stock_rows: int
    out_of_stock_rows: int
    zeroed_below_threshold_rows: int
    missing_inventory_zeroed_rows: int
    output_xml: str
    summary_json: str
    inventory_only_csv: str
    catalog_only_csv: str
    assumptions: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
