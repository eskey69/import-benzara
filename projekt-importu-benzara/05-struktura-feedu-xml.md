# Struktura Feedu XML

## Rekomendacja

Glowny feed powinien miec stabilna, plytka i czytelna strukture:

```xml
<catalog>
  <products>
    <product>
      ...
    </product>
  </products>
</catalog>
```

## Dlaczego taki uklad

- ulatwia wybor wezla produktu w pluginie,
- upraszcza XPath-y,
- jest czytelny dla czlowieka,
- dobrze wspiera wariacje zagniezdzone.

## Rekomendowany wezel produktu

- `catalog/products/product`

## Rekomendowane pola produktu

- `id`
- `type`
- `name`
- `sku`
- `ean`
- `description`
- `short_description`
- `pricing/regular`
- `pricing/sale`
- `pricing/tax_status`
- `pricing/tax_class`
- `stock/manage`
- `stock/qty`
- `stock/status`
- `stock/backorders`
- `stock/low_stock`
- `shipping/weight`
- `shipping/length`
- `shipping/width`
- `shipping/height`
- `shipping/class_id`
- `categories/category`
- `categories/tree`
- `tags/tag`
- `images/image`
- `attributes/attribute/name`
- `attributes/attribute/value`

## Rekomendowane pola wariacji

- `variations/variation/id`
- `variations/variation/sku`
- `variations/variation/ean`
- `variations/variation/price`
- `variations/variation/sale_price`
- `variations/variation/stock_qty`
- `variations/variation/stock_status`
- `variations/variation/images/image`
- `variations/variation/attributes/attribute/name`
- `variations/variation/attributes/attribute/value`

## Rekomendowane mapowanie w pluginie

### Produkt glowny

- tytul: `name`
- SKU: `sku`
- custom ID: `id`
- EAN: `ean`
- opis: `description`
- krotki opis: `short_description`
- cena: `pricing/regular`
- cena promocyjna: `pricing/sale`
- stock qty: `stock/qty`
- stock status: `stock/status`
- obrazy: `images/image`
- kategorie: `categories/category` albo `categories/tree`

### Produkt zmienny

Tryb:

- `Variable products are embedded as child tags in XML`

XPath wariacji:

- `variations/variation`

## Zasady generowania XML

- kodowanie UTF-8,
- opisy HTML w CDATA,
- liczby dziesietne z kropka,
- puste pola opcjonalne lepiej zostawiac jako pusty element niz losowy tekst,
- nie mieszac kilku znaczen w jednym polu, jesli mozna je rozdzielic na osobne tagi.

## Referencja

Przykladowy feed znajduje sie tutaj:

- [reference/recommended-dropshipping-feed.xml](C:/Users/skrupa/Documents/Benzara%20project/projekt-importu-benzara/reference/recommended-dropshipping-feed.xml)
