from __future__ import annotations

from pathlib import Path

from .config import AppConfig
from .loaders import load_catalog_xlsx, load_inventory_csv, normalize_text
from .models import GenerationSummary
from .reporting import write_csv, write_summary


def build_default_output_paths(output_csv: Path) -> tuple[Path, Path, Path]:
    stem = output_csv.stem
    parent = output_csv.parent
    summary_json = parent / f"{stem}.summary.json"
    inventory_only_csv = parent / f"{stem}.inventory-only.csv"
    catalog_only_csv = parent / f"{stem}.catalog-only.csv"
    return summary_json, inventory_only_csv, catalog_only_csv


def generate_feed(config: AppConfig) -> GenerationSummary:
    inventory = load_inventory_csv(
        path=config.inventory_csv,
        sku_column=config.sku_column,
        qty_column=config.quantity_column,
        delimiter=config.inventory_delimiter,
    )
    catalog = load_catalog_xlsx(
        path=config.catalog_xlsx,
        sku_column=config.sku_column,
        inventory_qty_column=config.catalog_inventory_qty_column,
    )

    output_headers = list(catalog.headers)
    if config.quantity_column not in output_headers:
        output_headers.append(config.quantity_column)

    matched_rows: list[dict[str, str]] = []
    catalog_only_rows: list[dict[str, str]] = []
    blank_catalog_skus = 0
    skipped_by_min_qty = 0
    seen_in_catalog_and_inventory: set[str] = set()

    title_header = next((header for header in catalog.headers if header.strip().lower() == "title"), None)

    for catalog_row in catalog.rows:
        sku = normalize_text(catalog_row.values.get(catalog.sku_header, ""))
        if sku == "":
            blank_catalog_skus += 1
            catalog_only_rows.append(
                {
                    "SKU": "",
                    "Title": catalog_row.values.get(title_header or "", ""),
                    "Reason": f"Blank SKU in catalog row {catalog_row.row_number}",
                }
            )
            continue

        qty = inventory.quantities.get(sku)
        if qty is None:
            catalog_only_rows.append(
                {
                    "SKU": sku,
                    "Title": catalog_row.values.get(title_header or "", ""),
                    "Reason": "Missing in inventory file",
                }
            )
            continue

        seen_in_catalog_and_inventory.add(sku)

        if config.min_qty is not None and qty <= config.min_qty:
            skipped_by_min_qty += 1
            continue

        output_row = dict(catalog_row.values)
        qty_text = str(qty)
        if config.sync_catalog_inventory_qty and catalog.inventory_qty_header is not None:
            output_row[catalog.inventory_qty_header] = qty_text
        output_row[config.quantity_column] = qty_text
        matched_rows.append(output_row)

    inventory_only_rows: list[dict[str, str]] = []
    for sku, qty in inventory.quantities.items():
        if sku not in seen_in_catalog_and_inventory:
            inventory_only_rows.append(
                {
                    "SKU": sku,
                    "Qty": str(qty),
                    "Reason": "Missing in catalog file",
                }
            )

    write_csv(config.output_csv, output_headers, matched_rows, config.output_delimiter)
    write_csv(config.inventory_only_csv, ["SKU", "Qty", "Reason"], inventory_only_rows, config.output_delimiter)
    write_csv(config.catalog_only_csv, ["SKU", "Title", "Reason"], catalog_only_rows, config.output_delimiter)

    summary = GenerationSummary(
        inventory_rows=inventory.row_count,
        catalog_rows=len(catalog.rows),
        matched_rows=len(matched_rows),
        inventory_only_rows=len(inventory_only_rows),
        catalog_only_rows=len(catalog_only_rows),
        invalid_inventory_rows=len(inventory.invalid_rows),
        duplicate_inventory_skus=len(inventory.duplicate_skus),
        blank_catalog_skus=blank_catalog_skus,
        skipped_by_min_qty=skipped_by_min_qty,
        output_csv=str(config.output_csv),
        summary_json=str(config.summary_json),
        inventory_only_csv=str(config.inventory_only_csv),
        catalog_only_csv=str(config.catalog_only_csv),
        assumptions=[
            "Only SKUs present in both files are exported.",
            "Existing catalog rows are preserved in original order.",
            "The catalog 'Inventory Qty' column is synchronized with the inventory CSV when present.",
            "A separate 'Qty' column is always included in the output for plugin mapping compatibility.",
            "Rows missing in one of the sources are reported in side-car CSV files instead of being silently dropped.",
        ],
    )
    write_summary(config.summary_json, summary)
    return summary
