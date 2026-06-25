from __future__ import annotations

from horpach_benzara.models import ProductDecision
from horpach_benzara.rules.pricing import compute_target_price
from horpach_benzara.rules.shipping import shipping_eligible


def build_decisions(
    woo_products: dict,
    supplier_products: dict,
    inventory_products: dict,
    config: dict,
) -> list[ProductDecision]:
    decisions: list[ProductDecision] = []
    all_skus = sorted(set(woo_products) | set(supplier_products) | set(inventory_products))

    for sku in all_skus:
        woo = woo_products.get(sku)
        supplier = supplier_products.get(sku)
        inventory = inventory_products.get(sku)

        title = ""
        if supplier and supplier.title:
            title = supplier.title
        elif inventory and inventory.title:
            title = inventory.title
        elif woo and woo.title:
            title = woo.title

        weight = None
        length = None
        width = None
        height = None
        if supplier:
            weight = supplier.ship_weight or supplier.product_weight
            length = supplier.ship_length or supplier.product_length
            width = supplier.ship_width or supplier.product_width
            height = supplier.ship_height or supplier.product_height
        elif inventory:
            weight = inventory.weight
            length = inventory.length
            width = inventory.width
            height = inventory.height
        elif woo:
            weight = woo.weight
            length = woo.length
            width = woo.width
            height = woo.height

        eligible, shipping_reason = shipping_eligible(
            weight=weight,
            length=length,
            width=width,
            height=height,
            config=config,
        )

        target_price = None
        if supplier:
            target_price = compute_target_price(supplier.wholesale_price, config)
        elif inventory:
            target_price = inventory.regular_price
        elif woo:
            target_price = woo.regular_price

        stock_quantity = inventory.stock_quantity if inventory else 0
        stock_status = "instock" if (stock_quantity or 0) > 0 else "outofstock"

        if woo and inventory:
            action = "update"
            reason = "matched_existing_product"
        elif (not woo) and supplier and inventory:
            action = "create"
            reason = "new_supplier_product"
        elif woo and not inventory:
            action = "update"
            reason = "missing_in_inventory_set_outofstock"
        else:
            action = "skip"
            reason = "missing_required_sources"

        if action == "create" and not eligible:
            action = "skip"
            reason = shipping_reason

        publish_status = config["publication"].get("new_products_status", "draft")
        if action == "create" and (stock_quantity or 0) < int(config["publication"].get("min_stock_to_publish", 1)):
            action = "skip"
            reason = "stock_below_publication_threshold"

        decisions.append(
            ProductDecision(
                normalized_sku=sku,
                action=action,
                reason=reason,
                woo_product_id=woo.product_id if woo else None,
                exists_in_woo=woo is not None,
                title=title,
                regular_price=target_price,
                stock_quantity=stock_quantity,
                stock_status=stock_status,
                weight=weight,
                length=length,
                width=width,
                height=height,
                shipping_eligible=eligible,
                publish_status="publish" if woo else publish_status,
                source_flags={
                    "woo": woo is not None,
                    "supplier": supplier is not None,
                    "inventory": inventory is not None,
                },
            )
        )

    return decisions

