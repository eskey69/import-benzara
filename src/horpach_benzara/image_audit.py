from __future__ import annotations

import argparse
import html
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import pandas as pd
import requests

from horpach_benzara.utils import normalize_sku


VALID_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
IMAGE_COLUMN_PATTERN = re.compile(r"^Image URL \d+$")
BENZARA_SEARCH_URL = "https://benzara.com/search"
BENZARA_SUGGEST_URL = "https://benzara.com/search/suggest.json"
BENZARA_BASE_URL = "https://benzara.com"
REQUEST_TIMEOUT_SECONDS = 20
BENZARA_RATE_LIMIT_SECONDS = 3.5
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0 Safari/537.36"


@dataclass(slots=True)
class AuditResult:
    original_image_url: str
    final_image_url: str
    image_status: str
    image_source: str
    image_recovery_method: str
    image_error: str


class RequestThrottle:
    def __init__(self, interval_seconds: float) -> None:
        self.interval_seconds = interval_seconds
        self._last_request_at: float | None = None

    def wait(self) -> None:
        if self._last_request_at is None:
            self._last_request_at = time.monotonic()
            return
        elapsed = time.monotonic() - self._last_request_at
        remaining = self.interval_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)
        self._last_request_at = time.monotonic()


class JsonCache:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError:
            return {}

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self.data, handle, ensure_ascii=False, indent=2)


class ImageAuditor:
    def __init__(self, cache_dir: Path) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": DEFAULT_USER_AGENT})
        self.checked_url_cache = JsonCache(cache_dir / "checked_urls.json")
        self.search_cache = JsonCache(cache_dir / "benzara_search_pages.json")
        self.product_cache = JsonCache(cache_dir / "benzara_product_images.json")
        self.benzara_throttle = RequestThrottle(BENZARA_RATE_LIMIT_SECONDS)

    def save_caches(self) -> None:
        self.checked_url_cache.save()
        self.search_cache.save()
        self.product_cache.save()

    def _normalize_content_type(self, value: str | None) -> str:
        if not value:
            return ""
        return value.split(";", 1)[0].strip().lower()

    def _validated_url(self, url: str) -> tuple[bool, str]:
        normalized_url = url.strip()
        if not normalized_url:
            return False, "empty_url"
        cached = self.checked_url_cache.data.get(normalized_url)
        if cached is not None:
            return bool(cached["valid"]), str(cached.get("error", ""))

        valid = False
        error = ""
        should_fallback_to_get = False
        try:
            response = self.session.head(
                normalized_url,
                allow_redirects=True,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            content_type = self._normalize_content_type(response.headers.get("Content-Type"))
            valid = response.status_code == 200 and content_type in VALID_CONTENT_TYPES
            if not valid:
                error = f"head_status_{response.status_code}_content_type_{content_type or 'unknown'}"
                should_fallback_to_get = response.status_code in {200, 403, 405} or not content_type
        except requests.RequestException as exc:
            error = f"head_error:{exc.__class__.__name__}"
            should_fallback_to_get = True

        if not valid and should_fallback_to_get:
            response = None
            try:
                response = self.session.get(
                    normalized_url,
                    allow_redirects=True,
                    stream=True,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
                content_type = self._normalize_content_type(response.headers.get("Content-Type"))
                valid = response.status_code == 200 and content_type in VALID_CONTENT_TYPES
                if not valid:
                    error = f"get_status_{response.status_code}_content_type_{content_type or 'unknown'}"
            except requests.RequestException as exc:
                error = f"get_error:{exc.__class__.__name__}"
            finally:
                try:
                    if response is not None:
                        response.close()
                except Exception:
                    pass

        self.checked_url_cache.data[normalized_url] = {"valid": valid, "error": error}
        return valid, error

    def _build_alt_urls(self, original_url: str) -> list[str]:
        parsed = urlparse(original_url)
        path = unquote(parsed.path)
        if not path:
            return []
        directory = path.rsplit("/", 1)[0]
        base_name = Path(path).stem
        urls: list[str] = []
        seen: set[str] = set()
        for extension in IMAGE_EXTENSIONS:
            candidate_path = f"{directory}/{base_name}{extension}"
            candidate_url = f"{parsed.scheme}://{parsed.netloc}{candidate_path}"
            if candidate_url not in seen:
                seen.add(candidate_url)
                urls.append(candidate_url)
        return urls

    def _extract_base_filename(self, original_url: str) -> str:
        path = unquote(urlparse(original_url).path)
        return Path(path).stem

    def _search_product_url(self, sku: str, title: str) -> str:
        cache_key = sku or title
        cached = self.search_cache.data.get(cache_key)
        if cached is not None:
            return str(cached)

        queries = [value for value in [sku, title] if value]
        product_url = ""
        for query in queries:
            self.benzara_throttle.wait()
            try:
                response = self.session.get(
                    BENZARA_SUGGEST_URL,
                    params={"q": query, "resources[type]": "product"},
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                data = response.json()
                products = data.get("resources", {}).get("results", {}).get("products", [])
                if products:
                    relative_url = products[0].get("url", "")
                    if relative_url:
                        product_url = urljoin(BENZARA_BASE_URL, html.unescape(relative_url))
                        break
            except (requests.RequestException, ValueError, KeyError):
                pass

            response = self.session.get(
                BENZARA_SEARCH_URL,
                params={"q": query},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            text = response.text
            matches = re.findall(r"/products/[^\"'\s<]+", text)
            if matches:
                product_url = urljoin(BENZARA_BASE_URL, html.unescape(matches[0]))
                break

        self.search_cache.data[cache_key] = product_url
        return product_url

    def _sort_candidate_urls(self, urls: list[str], base_filename: str) -> list[str]:
        def score(item: str) -> tuple[int, int, int, str]:
            unescaped = html.unescape(item)
            https_item = unescaped if unescaped.startswith("http") else f"https:{unescaped}"
            path_name = Path(urlparse(https_item).path).name
            stem = Path(path_name).stem
            prefix_match = 1 if stem.upper().startswith(base_filename.upper()) else 0
            exact_base_match = 1 if stem.upper() == base_filename.upper() else 0
            width_values = parse_qs(urlparse(https_item).query).get("width", ["0"])
            try:
                width_score = int(width_values[0])
            except ValueError:
                width_score = 0
            return (prefix_match, exact_base_match, width_score, https_item)

        return [url if url.startswith("http") else f"https:{html.unescape(url)}" for url in sorted(set(urls), key=score, reverse=True)]

    def _extract_cdn_urls(self, html_text: str) -> list[str]:
        urls = re.findall(r"(?:https?:)?//benzara\.com/cdn/shop/files/[^\"'\s<)]+", html_text)
        cleaned = []
        for url in urls:
            normalized = html.unescape(url)
            if normalized.startswith("//"):
                normalized = f"https:{normalized}"
            if Path(urlparse(normalized).path).suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            cleaned.append(normalized)
        return cleaned

    def _try_direct_product_page(self, sku: str, title: str) -> list[str]:
        slug_title = _slugify_product_title(title)
        slug_sku = sku.lower()
        candidate_url = f"{BENZARA_BASE_URL}/products/{slug_title}-{slug_sku}"
        self.benzara_throttle.wait()
        response = self.session.get(candidate_url, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code != 200:
            return []
        urls = self._extract_cdn_urls(response.text)
        matching_urls = []
        for url in urls:
            stem = Path(urlparse(url).path).stem.upper()
            if stem.startswith(sku.upper()):
                matching_urls.append(url)
        return matching_urls

    def _load_product_cdn_urls(self, sku: str, title: str) -> list[str]:
        cache_key = sku or title
        cached = self.product_cache.data.get(cache_key)
        if cached is not None:
            return list(cached)

        direct_urls = self._try_direct_product_page(sku, title)
        if direct_urls:
            self.product_cache.data[cache_key] = direct_urls
            return direct_urls

        product_url = self._search_product_url(sku, title)
        if not product_url:
            self.product_cache.data[cache_key] = []
            return []

        self.benzara_throttle.wait()
        response = self.session.get(product_url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        urls = self._extract_cdn_urls(response.text)
        self.product_cache.data[cache_key] = urls
        return urls

    def audit_image(self, *, sku: str, title: str, original_url: str) -> AuditResult:
        cleaned_original = str(original_url or "").strip()
        if not cleaned_original:
            return AuditResult(
                original_image_url="",
                final_image_url="",
                image_status="not_provided",
                image_source="none",
                image_recovery_method="",
                image_error="empty_source_url",
            )

        valid, error = self._validated_url(cleaned_original)
        if valid:
            return AuditResult(
                original_image_url=cleaned_original,
                final_image_url=cleaned_original,
                image_status="valid_original_url",
                image_source="source_file",
                image_recovery_method="",
                image_error="",
            )

        for candidate_url in self._build_alt_urls(cleaned_original):
            alt_valid, _ = self._validated_url(candidate_url)
            if alt_valid:
                return AuditResult(
                    original_image_url=cleaned_original,
                    final_image_url=candidate_url,
                    image_status="recovered_from_original_directory",
                    image_source="source_file",
                    image_recovery_method="extension_fallback",
                    image_error=error,
                )

        base_filename = self._extract_base_filename(cleaned_original)
        try:
            cdn_urls = self._load_product_cdn_urls(sku, title)
        except requests.RequestException as exc:
            return AuditResult(
                original_image_url=cleaned_original,
                final_image_url="",
                image_status="missing_manual_review",
                image_source="none",
                image_recovery_method="",
                image_error=f"benzara_lookup_error:{exc.__class__.__name__}",
            )

        sorted_candidates = self._sort_candidate_urls(cdn_urls, base_filename)
        for candidate_url in sorted_candidates:
            path_name = Path(urlparse(candidate_url).path).name
            stem = Path(path_name).stem
            if not stem.upper().startswith(base_filename.upper()):
                continue
            candidate_valid, _ = self._validated_url(candidate_url)
            if candidate_valid:
                return AuditResult(
                    original_image_url=cleaned_original,
                    final_image_url=candidate_url,
                    image_status="recovered_from_benzara_cdn",
                    image_source="benzara_shopify_cdn",
                    image_recovery_method="base_filename_prefix_match",
                    image_error=error,
                )

        return AuditResult(
            original_image_url=cleaned_original,
            final_image_url="",
            image_status="missing_manual_review",
            image_source="none",
            image_recovery_method="",
            image_error=error or "no_valid_candidate_found",
        )


def _load_woo_skus(path: Path) -> set[str]:
    import xml.etree.ElementTree as ET

    namespace = {"wp": "http://wordpress.org/export/1.2/"}

    def clean(text: str | None) -> str:
        return (text or "").strip()

    skus: set[str] = set()
    for _, item in ET.iterparse(path, events=("end",)):
        if not item.tag.endswith("item"):
            continue
        post_type = clean(item.findtext("wp:post_type", default="", namespaces=namespace))
        if post_type != "product":
            item.clear()
            continue
        sku = ""
        for meta in item.findall("wp:postmeta", namespace):
            key = clean(meta.findtext("wp:meta_key", default="", namespaces=namespace))
            if key in {"_sku", "sku"}:
                sku = normalize_sku(clean(meta.findtext("wp:meta_value", default="", namespaces=namespace)))
                if sku:
                    break
        if sku:
            skus.add(sku)
        item.clear()
    return skus


def _slugify_product_title(title: str) -> str:
    lowered = title.lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered)
    return lowered.strip("-")


def _image_columns(df: pd.DataFrame) -> list[str]:
    return sorted([column for column in df.columns if IMAGE_COLUMN_PATTERN.match(column)], key=lambda value: int(value.split()[-1]))


def _drop_image_columns(df: pd.DataFrame) -> pd.DataFrame:
    image_columns = _image_columns(df)
    return df.drop(columns=image_columns, errors="ignore")


def _new_and_existing_products(products_df: pd.DataFrame, woo_skus: set[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    working_df = products_df.copy()
    working_df["normalized_sku"] = working_df["SKU"].map(normalize_sku)
    working_df["exists_in_woo"] = working_df["normalized_sku"].isin(woo_skus)
    new_df = working_df.loc[~working_df["exists_in_woo"]].copy()
    existing_df = working_df.loc[working_df["exists_in_woo"]].copy()
    return new_df, existing_df


def _audit_new_products(new_df: pd.DataFrame, auditor: ImageAuditor) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    image_columns = _image_columns(new_df)
    if not image_columns:
        raise ValueError("No image columns found in products_allowed.csv.")

    audit_rows: list[dict[str, Any]] = []
    create_rows: list[dict[str, Any]] = []
    manual_review_rows: list[dict[str, Any]] = []

    for index, (_, row) in enumerate(new_df.iterrows(), start=1):
        product_record = row.to_dict()
        product_record["image_manual_review_required"] = False
        product_record["image_audit_summary"] = ""

        product_audit_parts: list[str] = []
        for column in image_columns:
            original_value = row.get(column)
            original_url = "" if pd.isna(original_value) else str(original_value).strip()
            audit = auditor.audit_image(
                sku=normalize_sku(row.get("SKU")),
                title=str(row.get("Title") or "").strip(),
                original_url=original_url,
            )
            audit_rows.append(
                {
                    "SKU": row.get("SKU", ""),
                    "Title": row.get("Title", ""),
                    "image_column": column,
                    "original_image_url": audit.original_image_url,
                    "final_image_url": audit.final_image_url,
                    "image_status": audit.image_status,
                    "image_source": audit.image_source,
                    "image_recovery_method": audit.image_recovery_method,
                    "image_error": audit.image_error,
                }
            )

            product_record[column] = audit.final_image_url
            product_audit_parts.append(f"{column}:{audit.image_status}")
            if audit.image_status == "missing_manual_review":
                product_record["image_manual_review_required"] = True

        product_record["image_audit_summary"] = "; ".join(product_audit_parts)
        if product_record["image_manual_review_required"]:
            manual_review_rows.append(product_record.copy())
        create_rows.append(product_record)
        if index % 10 == 0:
            auditor.save_caches()

    create_df = pd.DataFrame(create_rows)
    audit_df = pd.DataFrame(audit_rows)
    manual_review_df = pd.DataFrame(manual_review_rows)
    return create_df, audit_df, manual_review_df


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and recover image URLs for new Benzara products before WooCommerce import."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("output/products_allowed.csv"),
        help="Input CSV with allowed Benzara products.",
    )
    parser.add_argument(
        "--woo-xml",
        type=Path,
        default=Path("data/inbox/horpachcom.WordPress.2026-06-24.xml"),
        help="WooCommerce WordPress export used to detect existing products.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Output directory for image audit files.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path("output/cache"),
        help="Cache directory for checked URLs and Benzara pages.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    input_path = args.input.resolve()
    woo_xml_path = args.woo_xml.resolve()
    output_dir = args.output_dir.resolve()
    cache_dir = args.cache_dir.resolve()

    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    products_df = pd.read_csv(input_path, encoding="utf-8-sig")
    woo_skus = _load_woo_skus(woo_xml_path)
    new_df, existing_df = _new_and_existing_products(products_df, woo_skus)

    auditor = ImageAuditor(cache_dir=cache_dir)
    create_df, audit_df, manual_review_df = _audit_new_products(new_df, auditor)
    auditor.save_caches()

    existing_export_df = _drop_image_columns(existing_df).drop(columns=["normalized_sku", "exists_in_woo"], errors="ignore")
    create_export_df = create_df.drop(columns=["normalized_sku", "exists_in_woo"], errors="ignore")
    manual_review_export_df = manual_review_df.drop(columns=["normalized_sku", "exists_in_woo"], errors="ignore")

    create_path = output_dir / "products_create_with_images.csv"
    update_path = output_dir / "products_update_without_images.csv"
    audit_path = output_dir / "products_new_image_audit.csv"
    manual_review_path = output_dir / "products_new_manual_image_review.csv"

    create_export_df.to_csv(create_path, index=False, encoding="utf-8-sig")
    existing_export_df.to_csv(update_path, index=False, encoding="utf-8-sig")
    audit_df.to_csv(audit_path, index=False, encoding="utf-8-sig")
    manual_review_export_df.to_csv(manual_review_path, index=False, encoding="utf-8-sig")

    print(f"Input rows: {len(products_df)}")
    print(f"New products: {len(new_df)}")
    print(f"Existing products: {len(existing_df)}")
    print(f"Create CSV: {create_path}")
    print(f"Update CSV: {update_path}")
    print(f"Image audit CSV: {audit_path}")
    print(f"Manual review CSV: {manual_review_path}")
    print(f"Audit rows: {len(audit_df)}")
    print(f"Manual review rows: {len(manual_review_export_df)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
