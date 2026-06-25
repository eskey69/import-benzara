from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(slots=True)
class WooProduct:
    product_id: str
    title: str
    sku: str
    status: str
    regular_price: Decimal | None = None
    stock_quantity: int | None = None
    stock_status: str | None = None
    weight: Decimal | None = None
    length: Decimal | None = None
    width: Decimal | None = None
    height: Decimal | None = None
    raw_meta: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class SupplierCatalogProduct:
    sku: str
    title: str
    description: str
    wholesale_price: Decimal | None
    product_weight: Decimal | None
    product_length: Decimal | None
    product_width: Decimal | None
    product_height: Decimal | None
    ship_weight: Decimal | None
    ship_length: Decimal | None
    ship_width: Decimal | None
    ship_height: Decimal | None
    brand: str | None = None
    category: str | None = None
    source_row: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class InventoryProduct:
    sku: str
    title: str
    regular_price: Decimal | None
    stock_quantity: int | None
    stock_status: str | None
    weight: Decimal | None
    length: Decimal | None
    width: Decimal | None
    height: Decimal | None


@dataclass(slots=True)
class ProductDecision:
    normalized_sku: str
    action: str
    reason: str
    woo_product_id: str | None
    exists_in_woo: bool
    title: str
    regular_price: Decimal | None
    stock_quantity: int | None
    stock_status: str
    weight: Decimal | None
    length: Decimal | None
    width: Decimal | None
    height: Decimal | None
    shipping_eligible: bool
    publish_status: str
    source_flags: dict[str, bool] = field(default_factory=dict)

