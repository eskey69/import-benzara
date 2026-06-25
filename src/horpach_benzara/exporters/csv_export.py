from __future__ import annotations

import csv
from pathlib import Path

from horpach_benzara.models import ProductDecision


def export_decisions_csv(path: Path, decisions: list[ProductDecision]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "sku",
                "action",
                "reason",
                "woo_product_id",
                "exists_in_woo",
                "title",
                "regular_price",
                "stock_quantity",
                "stock_status",
                "weight",
                "length",
                "width",
                "height",
                "shipping_eligible",
                "publish_status",
                "source_woo",
                "source_supplier",
                "source_inventory",
            ],
        )
        writer.writeheader()
        for item in decisions:
            writer.writerow(
                {
                    "sku": item.normalized_sku,
                    "action": item.action,
                    "reason": item.reason,
                    "woo_product_id": item.woo_product_id or "",
                    "exists_in_woo": str(item.exists_in_woo).lower(),
                    "title": item.title,
                    "regular_price": item.regular_price or "",
                    "stock_quantity": item.stock_quantity if item.stock_quantity is not None else "",
                    "stock_status": item.stock_status,
                    "weight": item.weight or "",
                    "length": item.length or "",
                    "width": item.width or "",
                    "height": item.height or "",
                    "shipping_eligible": str(item.shipping_eligible).lower(),
                    "publish_status": item.publish_status,
                    "source_woo": str(item.source_flags.get("woo", False)).lower(),
                    "source_supplier": str(item.source_flags.get("supplier", False)).lower(),
                    "source_inventory": str(item.source_flags.get("inventory", False)).lower(),
                }
            )

