import unittest
from decimal import Decimal

from horpach_benzara.rules.shipping import shipping_eligible


class ShippingTests(unittest.TestCase):
    def test_shipping_eligible_accepts_dimensions_within_limits(self) -> None:
        config = {
            "shipping_limits": {
                "max_weight": 30,
                "max_length": 120,
                "max_width": 80,
                "max_height": 80,
                "max_dimension_sum": 250,
            }
        }
        allowed, reason = shipping_eligible(
            weight=Decimal("12"),
            length=Decimal("40"),
            width=Decimal("30"),
            height=Decimal("20"),
            config=config,
        )
        self.assertTrue(allowed)
        self.assertEqual(reason, "ok")


if __name__ == "__main__":
    unittest.main()
