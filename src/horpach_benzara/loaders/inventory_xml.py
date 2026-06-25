from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from horpach_benzara.models import InventoryProduct
from horpach_benzara.utils import clean_text, normalize_sku, to_decimal, to_int


def _find_text(element: ET.Element, path: str) -> str:
    node = element.find(path)
    return clean_text(node.text if node is not None else "")


def load_inventory_products(path: Path) -> dict[str, InventoryProduct]:
    products: dict[str, InventoryProduct] = {}
    for _, product in ET.iterparse(path, events=("end",)):
        if product.tag != "product":
            continue

        sku = normalize_sku(_find_text(product, "sku"))
        if not sku:
            product.clear()
            continue

        products[sku] = InventoryProduct(
            sku=sku,
            title=_find_text(product, "name"),
            regular_price=to_decimal(_find_text(product, "pricing/regular")),
            stock_quantity=to_int(_find_text(product, "stock/qty")),
            stock_status=_find_text(product, "stock/status") or None,
            weight=to_decimal(_find_text(product, "shipping/weight")),
            length=to_decimal(_find_text(product, "shipping/length")),
            width=to_decimal(_find_text(product, "shipping/width")),
            height=to_decimal(_find_text(product, "shipping/height")),
        )
        product.clear()
    return products

