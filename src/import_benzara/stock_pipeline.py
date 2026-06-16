from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from .config import StockFeedConfig
from .loaders import load_catalog_xlsx, load_inventory_csv, normalize_text, resolve_header
from .models import StockFeedSummary
from .reporting import write_csv, write_stock_summary, write_text


def build_default_stock_output_paths(output_xml: Path) -> tuple[Path, Path, Path]:
    stem = output_xml.stem
    parent = output_xml.parent
    summary_json = parent / f"{stem}.summary.json"
    inventory_only_csv = parent / f"{stem}.inventory-only.csv"
    catalog_only_csv = parent / f"{stem}.catalog-only.csv"
    return summary_json, inventory_only_csv, catalog_only_csv


def _build_stock_feed_xml(rows: list[dict[str, str]]) -> str:
    catalog = ET.Element("catalog")
    products = ET.SubElement(catalog, "products")

    for row in rows:
        product = ET.SubElement(products, "product")
        ET.SubElement(product, "sku").text = row["sku"]
        stock = ET.SubElement(product, "stock")
        ET.SubElement(stock, "manage").text = "true"
        ET.SubElement(stock, "qty").text = row["qty"]
        ET.SubElement(stock, "status").text = row["status"]

    tree = ET.ElementTree(catalog)
    ET.indent(tree, space="  ")
    return ET.tostring(catalog, encoding="utf-8", xml_declaration=True).decode("utf-8")


def generate_stock_feed(config: StockFeedConfig) -> StockFeedSummary:
    inventory = load_inventory_csv(
        path=config.inventory_csv,
        sku_column=config.sku_column,
        qty_column=config.quantity_column,
        delimiter=config.inventory_delimiter,
    )
    if inventory.conflicting_duplicate_skus:
        conflict = inventory.conflicting_duplicate_skus[0]
        raise ValueError(
            "Inventory file contains conflicting duplicate SKU values. "
            f"First conflict: row {conflict.row_number}, SKU {conflict.sku}"
        )

    catalog = load_catalog_xlsx(
        path=config.catalog_xlsx,
        sku_column=config.sku_column,
        inventory_qty_column="Inventory Qty",
    )

    title_header = resolve_header(catalog.headers, config.title_column) or config.title_column

    stock_rows: list[dict[str, str]] = []
    catalog_only_rows: list[dict[str, str]] = []
    inventory_only_rows: list[dict[str, str]] = []

    blank_catalog_skus = 0
    in_stock_rows = 0
    out_of_stock_rows = 0
    zeroed_below_threshold_rows = 0
    missing_inventory_zeroed_rows = 0
    seen_inventory_skus: set[str] = set()

    for catalog_row in catalog.rows:
        sku = normalize_text(catalog_row.values.get(catalog.sku_header, ""))
        title = normalize_text(catalog_row.values.get(title_header, ""))

        if sku == "":
            blank_catalog_skus += 1
            catalog_only_rows.append(
                {
                    "SKU": "",
                    "Title": title,
                    "Reason": f"Blank SKU in catalog row {catalog_row.row_number}",
                }
            )
            continue

        source_qty = inventory.quantities.get(sku)
        if source_qty is None:
            effective_qty = 0
            missing_inventory_zeroed_rows += 1
            catalog_only_rows.append(
                {
                    "SKU": sku,
                    "Title": title,
                    "Reason": "Missing in inventory file; exported as outofstock",
                }
            )
        else:
            seen_inventory_skus.add(sku)
            effective_qty = source_qty if source_qty >= config.minimum_stock_threshold else 0
            if effective_qty == 0 and source_qty < config.minimum_stock_threshold:
                zeroed_below_threshold_rows += 1

        status = "instock" if effective_qty > 0 else "outofstock"
        if effective_qty > 0:
            in_stock_rows += 1
        else:
            out_of_stock_rows += 1

        stock_rows.append({"sku": sku, "qty": str(effective_qty), "status": status})

    for sku, qty in inventory.quantities.items():
        if sku not in seen_inventory_skus:
            inventory_only_rows.append({"SKU": sku, "Qty": str(qty), "Reason": "Missing in catalog file"})

    xml_content = _build_stock_feed_xml(stock_rows)
    write_text(config.output_xml, xml_content)
    write_csv(config.inventory_only_csv, ["SKU", "Qty", "Reason"], inventory_only_rows, ";")
    write_csv(config.catalog_only_csv, ["SKU", "Title", "Reason"], catalog_only_rows, ";")

    summary = StockFeedSummary(
        catalog_file=str(config.catalog_xlsx),
        inventory_file=str(config.inventory_csv),
        stock_threshold=config.minimum_stock_threshold,
        inventory_rows=inventory.row_count,
        catalog_rows=len(catalog.rows),
        exported_rows=len(stock_rows),
        inventory_only_rows=len(inventory_only_rows),
        catalog_only_rows=len(catalog_only_rows),
        invalid_inventory_rows=len(inventory.invalid_rows),
        duplicate_inventory_rows=len(inventory.duplicate_skus),
        conflicting_duplicate_inventory_rows=len(inventory.conflicting_duplicate_skus),
        blank_catalog_skus=blank_catalog_skus,
        in_stock_rows=in_stock_rows,
        out_of_stock_rows=out_of_stock_rows,
        zeroed_below_threshold_rows=zeroed_below_threshold_rows,
        missing_inventory_zeroed_rows=missing_inventory_zeroed_rows,
        output_xml=str(config.output_xml),
        summary_json=str(config.summary_json),
        inventory_only_csv=str(config.inventory_only_csv),
        catalog_only_csv=str(config.catalog_only_csv),
        assumptions=[
            "Every catalog SKU is exported to the stock feed unless the catalog row has a blank SKU.",
            "Inventory quantities lower than the threshold are exported as 0.",
            "Catalog SKUs missing in the inventory file are exported as outofstock.",
            "Inventory SKUs missing in the catalog are reported but not exported.",
            "The XML feed is intended to update stock fields only, identified by SKU.",
        ],
    )
    write_stock_summary(config.summary_json, summary)
    return summary
