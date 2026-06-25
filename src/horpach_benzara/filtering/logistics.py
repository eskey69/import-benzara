from __future__ import annotations

from dataclasses import dataclass
from math import isnan

import pandas as pd


MAX_SHIP_WEIGHT = 30.0
MAX_SHIP_LENGTH = 48.0
MAX_SHIP_WIDTH = 24.0
MAX_SHIP_HEIGHT = 24.0
MAX_DIMENSION_SUM = 84.0

PREFERRED_SHIP_WEIGHT = 20.0
PREFERRED_SHIP_LENGTH = 36.0
PREFERRED_SHIP_WIDTH = 20.0
PREFERRED_SHIP_HEIGHT = 20.0
PREFERRED_DIMENSION_SUM = 72.0

SHIP_TYPE_BLOCKLIST = ("ltl", "freight", "freight quote")
MIN_INVENTORY_QTY = 10

UNUSED_OUTPUT_COLUMNS = [
    "Product Weight 2",
    "Product Length 2",
    "Product Width 2",
    "Product Height 2",
    "Product Weight 3",
    "Product Length 3",
    "Product Width 3",
    "Product Height 3",
    "Product Weight 4",
    "Product Length 4",
    "Product Width 4",
    "Product Height 4",
    "Product Weight 5",
    "Product Length 5",
    "Product Width 5",
    "Product Height 5",
    "Ship Weight 2",
    "Ship Length 2",
    "Ship Width 2",
    "Ship Height 2",
    "Ship Weight 3",
    "Ship Length 3",
    "Ship Width 3",
    "Ship Height 3",
    "Ship Weight 4",
    "Ship Length 4",
    "Ship Width 4",
    "Ship Height 4",
    "Ship Weight 5",
    "Ship Length 5",
    "Ship Width 5",
    "Ship Height 5",
    "Ship Weight 6",
    "Ship Length 6",
    "Ship Width 6",
    "Ship Height 6",
    "Ship Weight 7",
    "Ship Length 7",
    "Ship Width 7",
    "Ship Height 7",
]


@dataclass(slots=True)
class PackageMetrics:
    max_ship_weight: float
    max_ship_length: float
    max_ship_width: float
    max_ship_height: float
    max_dimension_sum: float


def _normalize_number(value: object) -> float:
    if value is None:
        return 0.0
    if isinstance(value, float) and isnan(value):
        return 0.0
    text = str(value).strip()
    if not text:
        return 0.0
    text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return 0.0


def _safe_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and isnan(value):
        return ""
    return str(value).strip()


def _collect_metrics(row: pd.Series) -> PackageMetrics:
    weight = _normalize_number(row.get("Ship Weight 1"))
    length = _normalize_number(row.get("Ship Length 1"))
    width = _normalize_number(row.get("Ship Width 1"))
    height = _normalize_number(row.get("Ship Height 1"))
    return PackageMetrics(
        max_ship_weight=weight,
        max_ship_length=length,
        max_ship_width=width,
        max_ship_height=height,
        max_dimension_sum=length + width + height,
    )


def _build_remove_reasons(row: pd.Series, metrics: PackageMetrics) -> list[str]:
    reasons: list[str] = []

    ship_type = _safe_text(row.get("Ship Type Small Package/LTL")).lower()
    number_of_boxes = _normalize_number(row.get("Number Of Boxes"))
    inventory_qty = _normalize_number(row.get("Inventory Qty"))

    if metrics.max_ship_weight > MAX_SHIP_WEIGHT:
        reasons.append("ship_weight_gt_30")
    if metrics.max_ship_length > MAX_SHIP_LENGTH:
        reasons.append("ship_length_gt_48")
    if metrics.max_ship_width > MAX_SHIP_WIDTH:
        reasons.append("ship_width_gt_24")
    if metrics.max_ship_height > MAX_SHIP_HEIGHT:
        reasons.append("ship_height_gt_24")
    if metrics.max_dimension_sum > MAX_DIMENSION_SUM:
        reasons.append("dimension_sum_gt_84")
    if number_of_boxes > 1:
        reasons.append("boxes_gt_1")
    if any(blocked in ship_type for blocked in SHIP_TYPE_BLOCKLIST):
        reasons.append("ship_type_not_small_package")
    if inventory_qty < MIN_INVENTORY_QTY:
        reasons.append("inventory_lt_10")

    return reasons


def _drop_unused_columns(df: pd.DataFrame) -> pd.DataFrame:
    columns_to_drop = [column for column in UNUSED_OUTPUT_COLUMNS if column in df.columns]
    if not columns_to_drop:
        return df
    return df.drop(columns=columns_to_drop)


def _build_logistics_status(row: pd.Series, metrics: PackageMetrics) -> str:
    ship_type = _safe_text(row.get("Ship Type Small Package/LTL")).lower()
    number_of_boxes = _normalize_number(row.get("Number Of Boxes"))

    preferred = (
        metrics.max_ship_weight <= PREFERRED_SHIP_WEIGHT
        and metrics.max_ship_length <= PREFERRED_SHIP_LENGTH
        and metrics.max_ship_width <= PREFERRED_SHIP_WIDTH
        and metrics.max_ship_height <= PREFERRED_SHIP_HEIGHT
        and metrics.max_dimension_sum <= PREFERRED_DIMENSION_SUM
        and number_of_boxes <= 1
        and "small package" in ship_type
    )
    return "preferred" if preferred else "allowed"


def split_by_logistics(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    required_columns = ["Ship Weight 1", "Ship Length 1", "Ship Width 1", "Ship Height 1"]
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required shipping columns: {missing_text}")

    annotated_rows = []
    removed_rows = []

    for _, row in df.iterrows():
        metrics = _collect_metrics(row)
        remove_reasons = _build_remove_reasons(row, metrics)

        annotated = row.to_dict()
        annotated["max_ship_weight"] = metrics.max_ship_weight
        annotated["max_ship_length"] = metrics.max_ship_length
        annotated["max_ship_width"] = metrics.max_ship_width
        annotated["max_ship_height"] = metrics.max_ship_height
        annotated["max_dimension_sum"] = metrics.max_dimension_sum

        if remove_reasons:
            removed_rows.append(
                {
                    "SKU": _safe_text(row.get("SKU")),
                    "Title": _safe_text(row.get("Title")),
                    "Ship Type Small Package/LTL": _safe_text(row.get("Ship Type Small Package/LTL")),
                    "Number Of Boxes": _normalize_number(row.get("Number Of Boxes")),
                    "max_ship_weight": metrics.max_ship_weight,
                    "max_ship_length": metrics.max_ship_length,
                    "max_ship_width": metrics.max_ship_width,
                    "max_ship_height": metrics.max_ship_height,
                    "max_dimension_sum": metrics.max_dimension_sum,
                    "remove_reason": "; ".join(remove_reasons),
                }
            )
        else:
            annotated["logistics_status"] = _build_logistics_status(row, metrics)
            annotated_rows.append(annotated)

    allowed_df = _drop_unused_columns(pd.DataFrame(annotated_rows))
    removed_df = pd.DataFrame(removed_rows)
    return allowed_df, removed_df
