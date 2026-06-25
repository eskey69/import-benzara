from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from horpach_benzara.filtering.logistics import split_by_logistics


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Filter Benzara XLSX catalog by logistics constraints before WooCommerce import."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/inbox/FTP Benzara JUNE (15-06-2026).xlsx"),
        help="Path to the Benzara XLSX catalog.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory for generated CSV files.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    input_path = args.input.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(input_path, engine="openpyxl")
    allowed_df, removed_df = split_by_logistics(df)

    allowed_path = output_dir / "products_allowed.csv"
    removed_path = output_dir / "products_removed_logistics.csv"

    allowed_df.to_csv(allowed_path, index=False, encoding="utf-8-sig")
    removed_df.to_csv(removed_path, index=False, encoding="utf-8-sig")

    print(f"Input rows: {len(df)}")
    print(f"Allowed rows: {len(allowed_df)}")
    print(f"Removed rows: {len(removed_df)}")
    print(f"Allowed CSV: {allowed_path}")
    print(f"Removed CSV: {removed_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
