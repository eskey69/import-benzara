from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from horpach_benzara.config import load_config
from horpach_benzara.exporters.csv_export import export_decisions_csv
from horpach_benzara.loaders.inventory_xml import load_inventory_products
from horpach_benzara.loaders.woo_xml import load_woo_products
from horpach_benzara.loaders.xlsx_catalog import load_supplier_catalog
from horpach_benzara.matchers.merge import build_decisions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare WooCommerce update data from Woo XML, Benzara XLSX, and inventory XML.")
    parser.add_argument("--woo-xml", type=Path, required=True)
    parser.add_argument("--supplier-xlsx", type=Path, required=True)
    parser.add_argument("--inventory-xml", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()

    config = load_config(args.config)
    woo_products = load_woo_products(args.woo_xml)
    supplier_products = load_supplier_catalog(args.supplier_xlsx)
    inventory_products = load_inventory_products(args.inventory_xml)
    decisions = build_decisions(woo_products, supplier_products, inventory_products, config)
    export_decisions_csv(args.output, decisions)

    counts = Counter(item.action for item in decisions)
    print(f"Woo products: {len(woo_products)}")
    print(f"Supplier products: {len(supplier_products)}")
    print(f"Inventory products: {len(inventory_products)}")
    print(f"Output rows: {len(decisions)}")
    for action, count in sorted(counts.items()):
        print(f"{action}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
