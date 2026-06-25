from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def clean_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_sku(value: object) -> str:
    text = clean_text(value)
    return text.upper()


def to_decimal(value: object) -> Decimal | None:
    text = clean_text(value)
    if not text:
        return None
    text = text.replace(",", "").replace("$", "")
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def to_int(value: object) -> int | None:
    decimal_value = to_decimal(value)
    if decimal_value is None:
        return None
    return int(decimal_value)


def quantize_price(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

