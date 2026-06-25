import unittest
from decimal import Decimal

from horpach_benzara.utils import normalize_sku, to_decimal


class UtilsTests(unittest.TestCase):
    def test_normalize_sku_uppercases_and_trims(self) -> None:
        self.assertEqual(normalize_sku("  ab-12  "), "AB-12")

    def test_to_decimal_parses_currency_like_values(self) -> None:
        self.assertEqual(to_decimal("$1,234.50"), Decimal("1234.50"))


if __name__ == "__main__":
    unittest.main()
