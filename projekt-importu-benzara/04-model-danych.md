# Model Danych

## Zasada

Model danych aplikacji ma byc niezalezny od struktury pojedynczego dostawcy i niezalezny od UI pluginu WooCommerce.

## Encja Product

Minimalny rekomendowany model:

- `supplier_id`
- `product_id`
- `custom_product_id`
- `type`
- `name`
- `sku`
- `ean`
- `description_html`
- `short_description_html`
- `external_url`
- `button_text`
- `regular_price`
- `sale_price`
- `tax_status`
- `tax_class`
- `virtual`
- `manage_stock`
- `stock_qty`
- `stock_status`
- `backorders`
- `low_stock_amount`
- `sold_individually`
- `weight`
- `length`
- `width`
- `height`
- `shipping_class_code`
- `categories`
- `category_trees`
- `tags`
- `images`
- `attributes`
- `meta`
- `status_flags`
- `variations`

## Encja Variation

Rekomendowany model:

- `variation_id`
- `custom_product_id`
- `sku`
- `ean`
- `regular_price`
- `sale_price`
- `manage_stock`
- `stock_qty`
- `stock_status`
- `backorders`
- `weight`
- `length`
- `width`
- `height`
- `shipping_class_code`
- `description_html`
- `images`
- `attributes`
- `meta`

## Encja Attribute

- `name`
- `value`
- `is_taxonomy`
- `scope`

Gdzie `scope` moze oznaczac:

- `product`
- `variation`

## Encja Image

- `url`
- `position`
- `is_featured`
- `scope`

## Encja Category

Mozliwe reprezentacje:

- lista plaskich nazw,
- lista pelnych sciezek drzewa,
- mapa zewnetrzna -> docelowa.

## Klucze synchronizacji

Preferowana kolejnosc:

1. `custom_product_id`
2. `sku`
3. `ean`

Nie rekomenduje sie synchronizacji po nazwie.

## Wymagania spojnoscowe

- `custom_product_id` musi byc stabilny w czasie.
- `sku` musi byc unikalne globalnie tam, gdzie jest uzywane jako klucz.
- kazda wariacja musi miec unikalny zestaw atrybutow.
- produkt zmienny musi miec co najmniej jedna wariacje albo zostac zdegradowany do prostego.
