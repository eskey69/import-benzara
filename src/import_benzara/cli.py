from __future__ import annotations

import argparse
import os
from pathlib import Path

from .config import AppConfig, StockFeedConfig
from .pipeline import build_default_output_paths, generate_feed
from .stock_pipeline import build_default_stock_output_paths, generate_stock_feed
from .storage import build_app_paths, copy_run_to_latest, ensure_app_directories, latest_uploaded_file, new_run_id


def _default_data_root() -> Path:
    return Path(os.environ.get("IMPORT_BENZARA_DATA_DIR", Path.cwd() / "data"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="import-benzara",
        description="Generator pliku wsadowego Benzara dla WP Desk Dropshipping XML WooCommerce.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Wygeneruj plik wsadowy CSV.")
    generate_parser.add_argument("--inventory", required=True, type=Path, help="Sciezka do pliku Inventory CSV.")
    generate_parser.add_argument("--catalog", required=True, type=Path, help="Sciezka do pliku katalogowego XLSX.")
    generate_parser.add_argument("--output", required=True, type=Path, help="Sciezka do wyjsciowego pliku CSV.")
    generate_parser.add_argument("--summary-json", type=Path, help="Opcjonalna sciezka raportu JSON.")
    generate_parser.add_argument("--inventory-only-csv", type=Path, help="Opcjonalna sciezka raportu inventory-only.")
    generate_parser.add_argument("--catalog-only-csv", type=Path, help="Opcjonalna sciezka raportu catalog-only.")
    generate_parser.add_argument(
        "--inventory-delimiter",
        default=None,
        help="Separator wejsciowego Inventory CSV. Domyslnie autodetekcja.",
    )
    generate_parser.add_argument("--output-delimiter", default=";", help="Separator wyjsciowych plikow CSV. Domyslnie ';'.")
    generate_parser.add_argument("--min-qty", type=int, default=None, help="Eksportuj tylko rekordy z Qty wiekszym niz ta wartosc.")
    generate_parser.add_argument(
        "--skip-inventory-qty-sync",
        action="store_true",
        help="Nie nadpisuj kolumny 'Inventory Qty' w katalogu.",
    )

    stock_parser = subparsers.add_parser("generate-stock-feed", help="Wygeneruj feed XML do aktualizacji stocku.")
    stock_parser.add_argument("--inventory", required=True, type=Path, help="Sciezka do pliku Inventory CSV.")
    stock_parser.add_argument("--catalog", required=True, type=Path, help="Sciezka do pliku katalogowego XLSX.")
    stock_parser.add_argument("--output-xml", required=True, type=Path, help="Sciezka do wyjsciowego pliku XML.")
    stock_parser.add_argument("--summary-json", type=Path, help="Opcjonalna sciezka raportu JSON.")
    stock_parser.add_argument("--inventory-only-csv", type=Path, help="Opcjonalna sciezka raportu inventory-only.")
    stock_parser.add_argument("--catalog-only-csv", type=Path, help="Opcjonalna sciezka raportu catalog-only.")
    stock_parser.add_argument("--inventory-delimiter", default=None, help="Separator wejsciowego Inventory CSV.")
    stock_parser.add_argument(
        "--minimum-stock-threshold",
        type=int,
        default=10,
        help="Ponizej tej wartosci stock jest eksportowany jako 0. Domyslnie 10.",
    )

    latest_stock_parser = subparsers.add_parser(
        "generate-latest-stock-feed",
        help="Wygeneruj feed XML z najnowszych plikow uploadowanych do katalogu data.",
    )
    latest_stock_parser.add_argument("--data-root", type=Path, default=_default_data_root(), help="Katalog danych aplikacji.")
    latest_stock_parser.add_argument(
        "--minimum-stock-threshold",
        type=int,
        default=10,
        help="Ponizej tej wartosci stock jest eksportowany jako 0. Domyslnie 10.",
    )

    serve_parser = subparsers.add_parser("serve", help="Uruchom lokalnie panel WWW.")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host dla serwera developerskiego.")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port dla serwera developerskiego.")
    serve_parser.add_argument("--data-root", type=Path, default=_default_data_root(), help="Katalog danych aplikacji.")
    serve_parser.add_argument("--debug", action="store_true", help="Uruchom Flask w trybie debug.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate":
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

    if args.command == "generate-stock-feed":
        summary_json, inventory_only_csv, catalog_only_csv = build_default_stock_output_paths(args.output_xml)
        config = StockFeedConfig(
            inventory_csv=args.inventory,
            catalog_xlsx=args.catalog,
            output_xml=args.output_xml,
            summary_json=args.summary_json or summary_json,
            inventory_only_csv=args.inventory_only_csv or inventory_only_csv,
            catalog_only_csv=args.catalog_only_csv or catalog_only_csv,
            inventory_delimiter=args.inventory_delimiter,
            minimum_stock_threshold=args.minimum_stock_threshold,
        )
        summary = generate_stock_feed(config)
        print(f"Output XML: {summary.output_xml}")
        print(f"Summary JSON: {summary.summary_json}")
        print(f"Inventory-only CSV: {summary.inventory_only_csv}")
        print(f"Catalog-only CSV: {summary.catalog_only_csv}")
        print(
            "Counts: "
            f"inventory={summary.inventory_rows}, "
            f"catalog={summary.catalog_rows}, "
            f"exported={summary.exported_rows}, "
            f"instock={summary.in_stock_rows}, "
            f"outofstock={summary.out_of_stock_rows}"
        )
        return 0

    if args.command == "generate-latest-stock-feed":
        paths = build_app_paths(args.data_root)
        ensure_app_directories(paths)
        catalog = latest_uploaded_file(paths.uploads_catalog, (".xlsx",))
        inventory = latest_uploaded_file(paths.uploads_inventory, (".csv",))
        if catalog is None:
            parser.error(f"No catalog file found in {paths.uploads_catalog}")
        if inventory is None:
            parser.error(f"No inventory file found in {paths.uploads_inventory}")

        run_id = new_run_id()
        run_dir = paths.generated_runs / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        output_xml = run_dir / "feed.xml"
        summary_json = run_dir / "feed.summary.json"
        inventory_only_csv = run_dir / "feed.inventory-only.csv"
        catalog_only_csv = run_dir / "feed.catalog-only.csv"

        config = StockFeedConfig(
            inventory_csv=inventory,
            catalog_xlsx=catalog,
            output_xml=output_xml,
            summary_json=summary_json,
            inventory_only_csv=inventory_only_csv,
            catalog_only_csv=catalog_only_csv,
            minimum_stock_threshold=args.minimum_stock_threshold,
        )
        summary = generate_stock_feed(config)
        copy_run_to_latest(run_dir, paths.generated_latest)
        print(f"Latest feed XML: {paths.generated_latest / 'feed.xml'}")
        print(f"Run summary: {summary.summary_json}")
        return 0

    if args.command == "serve":
        os.environ["IMPORT_BENZARA_DATA_DIR"] = str(args.data_root)
        from .webapp import create_app

        app = create_app(data_root=args.data_root)
        app.run(host=args.host, port=args.port, debug=args.debug)
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 1
