from __future__ import annotations

import argparse
from pathlib import Path

from .config import AppConfig
from .pipeline import build_default_output_paths, generate_feed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="import-benzara",
        description="Generator pliku wsadowego Benzara dla WP Desk Dropshipping XML WooCommerce.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Wygeneruj plik wsadowy CSV.")
    generate_parser.add_argument("--inventory", required=True, type=Path, help="Ścieżka do pliku Inventory CSV.")
    generate_parser.add_argument("--catalog", required=True, type=Path, help="Ścieżka do pliku katalogowego XLSX.")
    generate_parser.add_argument("--output", required=True, type=Path, help="Ścieżka do wyjściowego pliku CSV.")
    generate_parser.add_argument("--summary-json", type=Path, help="Opcjonalna ścieżka raportu JSON.")
    generate_parser.add_argument("--inventory-only-csv", type=Path, help="Opcjonalna ścieżka raportu inventory-only.")
    generate_parser.add_argument("--catalog-only-csv", type=Path, help="Opcjonalna ścieżka raportu catalog-only.")
    generate_parser.add_argument(
        "--inventory-delimiter",
        default=None,
        help="Separator wejściowego Inventory CSV. Domyślnie autodetekcja.",
    )
    generate_parser.add_argument("--output-delimiter", default=";", help="Separator wyjściowych plików CSV. Domyślnie ';'.")
    generate_parser.add_argument("--min-qty", type=int, default=None, help="Eksportuj tylko rekordy z Qty większym niż ta wartość.")
    generate_parser.add_argument(
        "--skip-inventory-qty-sync",
        action="store_true",
        help="Nie nadpisuj kolumny 'Inventory Qty' w katalogu.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command != "generate":
        parser.error(f"Unsupported command: {args.command}")

    summary_json, inventory_only_csv, catalog_only_csv = build_default_output_paths(args.output)
    config = AppConfig(
        inventory_csv=args.inventory,
        catalog_xlsx=args.catalog,
        output_csv=args.output,
        summary_json=args.summary_json or summary_json,
        inventory_only_csv=args.inventory_only_csv or inventory_only_csv,
        catalog_only_csv=args.catalog_only_csv or catalog_only_csv,
        inventory_delimiter=args.inventory_delimiter,
        output_delimiter=args.output_delimiter,
        sync_catalog_inventory_qty=not args.skip_inventory_qty_sync,
        min_qty=args.min_qty,
    )

    summary = generate_feed(config)
    print(f"Output CSV: {summary.output_csv}")
    print(f"Summary JSON: {summary.summary_json}")
    print(f"Inventory-only CSV: {summary.inventory_only_csv}")
    print(f"Catalog-only CSV: {summary.catalog_only_csv}")
    print(
        "Counts: "
        f"inventory={summary.inventory_rows}, "
        f"catalog={summary.catalog_rows}, "
        f"matched={summary.matched_rows}, "
        f"inventory_only={summary.inventory_only_rows}, "
        f"catalog_only={summary.catalog_only_rows}"
    )
    return 0
