from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from horpach_benzara.models import WooProduct
from horpach_benzara.utils import clean_text, normalize_sku, to_decimal, to_int

WP_NAMESPACE = {"wp": "http://wordpress.org/export/1.2/"}


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1]


def _extract_meta(item: ET.Element) -> dict[str, str]:
    meta: dict[str, str] = {}
    for child in item.findall("wp:postmeta", WP_NAMESPACE):
        key = clean_text(child.findtext("wp:meta_key", default="", namespaces=WP_NAMESPACE))
        value = clean_text(child.findtext("wp:meta_value", default="", namespaces=WP_NAMESPACE))
        if key:
            meta[key] = value
    return meta


def load_woo_products(path: Path) -> dict[str, WooProduct]:
    products: dict[str, WooProduct] = {}
    for _, item in ET.iterparse(path, events=("end",)):
        if _local_name(item.tag) != "item":
            continue

        post_type = clean_text(item.findtext("wp:post_type", default="", namespaces=WP_NAMESPACE))
        if post_type != "product":
            item.clear()
            continue

        meta = _extract_meta(item)
        sku = normalize_sku(meta.get("_sku") or meta.get("sku"))
        if not sku:
            item.clear()
            continue

        product = WooProduct(
            product_id=clean_text(item.findtext("wp:post_id", default="", namespaces=WP_NAMESPACE)),
            title=clean_text(item.findtext("title")),
            sku=sku,
            status=clean_text(item.findtext("wp:status", default="", namespaces=WP_NAMESPACE)),
            regular_price=to_decimal(meta.get("_regular_price")),
            stock_quantity=to_int(meta.get("_stock")),
            stock_status=clean_text(meta.get("_stock_status")) or None,
            weight=to_decimal(meta.get("_weight")),
            length=to_decimal(meta.get("_length")),
            width=to_decimal(meta.get("_width")),
            height=to_decimal(meta.get("_height")),
            raw_meta=meta,
        )
        products[sku] = product
        item.clear()
    return products

