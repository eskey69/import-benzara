# Mapowanie danych

## Zrodla

### Plik A

`horpachcom.WordPress.2026-06-24.xml`

Rola:

- baza produktow juz istniejacych w WooCommerce

Do rozpoznania:

- czy SKU jest w `sku` czy `_sku`
- gdzie sa pola ceny, statusu i metadanych produktu

### Plik B

`FTP Benzara JUNE (15-06-2026).xlsx`

Rola:

- pelna oferta Benzara

Oczekiwane dane:

- SKU
- nazwa produktu
- cena zakupu lub cena bazowa
- waga
- wymiary
- opis lub inne pola pomocnicze

### Plik C

`latest.xml`

Rola:

- aktualne stany magazynowe

Oczekiwane dane:

- SKU
- ilosc dostepna
- ewentualnie status dostepnosci

## Pole wspolne

Program nie zaklada z gory jednej nazwy pola SKU.

Najpierw:

- wykrywa `sku` lub `_sku`
- mapuje wartosc do `normalized_sku`

## Model wewnetrzny

Po normalizacji dane powinny trafic do wspolnego modelu:

```text
normalized_sku
woo_product_id
woo_exists
supplier_name
supplier_cost
stock_quantity
weight
length
width
height
price_target
shipping_eligible
action
```

## Reguly wyjsciowe

### Aktualizacja produktu istniejacego

Warunek:

- SKU istnieje w pliku A i zostalo dopasowane do plikow B lub C

Skutek:

- aktualizacja ceny
- aktualizacja stanu

### Dodanie nowego produktu

Warunek:

- SKU istnieje w pliku B i C
- SKU nie istnieje w pliku A
- produkt przechodzi filtry wysylkowe

Skutek:

- przygotowanie rekordu do dodania

### Odrzucenie produktu

Warunek:

- brak SKU
- brak krytycznych danych
- przekroczone limity wysylki
- zbyt niska oplacalnosc

Skutek:

- wpis do raportu odrzuconych rekordow
