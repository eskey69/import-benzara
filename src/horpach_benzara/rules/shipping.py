from __future__ import annotations

from decimal import Decimal


def shipping_eligible(
    *,
    weight: Decimal | None,
    length: Decimal | None,
    width: Decimal | None,
    height: Decimal | None,
    config: dict,
) -> tuple[bool, str]:
    limits = config["shipping_limits"]

    if None in (weight, length, width, height):
        return False, "missing_shipping_dimensions"

    if weight > Decimal(str(limits["max_weight"])):
        return False, "weight_limit_exceeded"
    if length > Decimal(str(limits["max_length"])):
        return False, "length_limit_exceeded"
    if width > Decimal(str(limits["max_width"])):
        return False, "width_limit_exceeded"
    if height > Decimal(str(limits["max_height"])):
        return False, "height_limit_exceeded"
    if (length + width + height) > Decimal(str(limits["max_dimension_sum"])):
        return False, "dimension_sum_limit_exceeded"

    return True, "ok"

