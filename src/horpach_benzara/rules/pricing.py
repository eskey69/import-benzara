from __future__ import annotations

from decimal import Decimal

from horpach_benzara.utils import quantize_price


def compute_target_price(cost: Decimal | None, config: dict) -> Decimal | None:
    if cost is None:
        return None

    rule = config["price_rule"]
    mode = rule.get("mode", "multiplier")
    value = Decimal(str(rule.get("value", 1)))
    if mode == "multiplier":
        price = cost * value
    elif mode == "markup":
        price = cost + value
    else:
        raise ValueError(f"Unsupported price_rule mode: {mode}")

    rounded = quantize_price(price)
    round_to = rule.get("round_to")
    if round_to is None:
        return rounded

    round_to_decimal = Decimal(str(round_to))
    whole_part = int(rounded)
    if rounded == whole_part:
        return Decimal(whole_part) + round_to_decimal
    return Decimal(whole_part) + round_to_decimal

