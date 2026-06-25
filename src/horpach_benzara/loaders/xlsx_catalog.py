from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from horpach_benzara.models import SupplierCatalogProduct
from horpach_benzara.utils import clean_text, normalize_sku, to_decimal

SHEET_NAMESPACE = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def _column_ref(cell_ref: str) -> str:
    letters = []
    for char in cell_ref:
        if char.isalpha():
            letters.append(char)
        else:
            break
    return "".join(letters)


def _read_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for item in root.findall("m:si", SHEET_NAMESPACE):
        text = "".join(node.text or "" for node in item.iterfind(".//m:t", SHEET_NAMESPACE))
        strings.append(text)
    return strings


def _first_sheet_path(zf: zipfile.ZipFile) -> str:
    workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rel_map = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall("rel:Relationship", SHEET_NAMESPACE)
    }
    first_sheet = workbook.find("m:sheets/m:sheet", SHEET_NAMESPACE)
    if first_sheet is None:
        raise ValueError("Workbook does not contain any sheets.")
    rel_id = first_sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
    target = rel_map[rel_id]
    return target if target.startswith("xl/") else f"xl/{target}"


def _decode_cell(cell: ET.Element, shared_strings: list[str]) -> str:
    value = cell.find("m:v", SHEET_NAMESPACE)
    if value is None or value.text is None:
        return ""
    cell_type = cell.attrib.get("t")
    if cell_type == "s":
        return shared_strings[int(value.text)]
    return value.text


def load_supplier_catalog(path: Path) -> dict[str, SupplierCatalogProduct]:
    products: dict[str, SupplierCatalogProduct] = {}
    with zipfile.ZipFile(path) as zf:
        shared_strings = _read_shared_strings(zf)
        sheet_path = _first_sheet_path(zf)

        headers: dict[str, str] = {}
        sheet_stream = zf.open(sheet_path)
        try:
            for _, row in ET.iterparse(sheet_stream, events=("end",)):
                if row.tag != "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row":
                    continue

                row_values: dict[str, str] = {}
                for cell in row.findall("m:c", SHEET_NAMESPACE):
                    row_values[_column_ref(cell.attrib["r"])] = _decode_cell(cell, shared_strings)

                row_number = int(row.attrib["r"])
                if row_number == 1:
                    headers = row_values
                    row.clear()
                    continue

                values_by_name = {headers[col]: value for col, value in row_values.items() if col in headers}
                sku = normalize_sku(values_by_name.get("SKU"))
                if not sku:
                    row.clear()
                    continue

                products[sku] = SupplierCatalogProduct(
                    sku=sku,
                    title=clean_text(values_by_name.get("Title")),
                    description=clean_text(values_by_name.get("Description")),
                    wholesale_price=to_decimal(values_by_name.get("Wholesale Price")),
                    product_weight=to_decimal(values_by_name.get("Product Weight 1")),
                    product_length=to_decimal(values_by_name.get("Product Length 1")),
                    product_width=to_decimal(values_by_name.get("Product Width 1")),
                    product_height=to_decimal(values_by_name.get("Product Height 1")),
                    ship_weight=to_decimal(values_by_name.get("Ship Weight 1")),
                    ship_length=to_decimal(values_by_name.get("Ship Length 1")),
                    ship_width=to_decimal(values_by_name.get("Ship Width 1")),
                    ship_height=to_decimal(values_by_name.get("Ship Height 1")),
                    brand=clean_text(values_by_name.get("Brand")) or None,
                    category=clean_text(values_by_name.get("Category")) or None,
                    source_row=values_by_name,
                )
                row.clear()
        finally:
            sheet_stream.close()

    return products

