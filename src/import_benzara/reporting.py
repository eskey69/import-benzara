from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import GenerationSummary, StockFeedSummary


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, headers: list[str], rows: list[dict[str, str]], delimiter: str) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter=delimiter, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary(path: Path, summary: GenerationSummary) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        json.dump(summary.to_dict(), handle, ensure_ascii=False, indent=2)


def write_stock_summary(path: Path, summary: StockFeedSummary) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        json.dump(summary.to_dict(), handle, ensure_ascii=False, indent=2)


def write_text(path: Path, content: str) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(content)
