# horpach-benzara

Aplikacja do przetwarzania danych produktowych z trzech plikow zrodlowych:

- `horpachcom.WordPress.2026-06-24.xml` - eksport WooCommerce jako plik bazowy
- `FTP Benzara JUNE (15-06-2026).xlsx` - pelna oferta Benzara
- `latest.xml` - aktualne stany magazynowe

## Cel projektu

Program ma przygotowac plik wynikowy `d`, ktory pozwoli:

- zaktualizowac stany magazynowe
- zaktualizowac ceny
- dodac nowe produkty
- pominac produkty nieoplacalne do wysylki na podstawie wagi i wymiarow

## Glowna zasada laczenia danych

Produkty sa laczone po SKU, ale program najpierw wykrywa, czy pole z identyfikatorem wystepuje jako:

- `sku`
- `_sku`

Po wykryciu dane sa normalizowane do jednego pola wewnetrznego: `normalized_sku`.

## Plan przetwarzania

1. Wczytanie pliku WooCommerce XML jako bazy istniejacych produktow.
2. Wczytanie pliku XLSX Benzara z pelna oferta.
3. Wczytanie pliku XML ze stanami magazynowymi.
4. Wykrycie pola SKU w kazdym z plikow.
5. Ujednolicenie danych do wspolnego modelu.
6. Polaczenie rekordow po `normalized_sku`.
7. Zastosowanie regul cen, stanow i kwalifikacji wysylkowej.
8. Wygenerowanie pliku wynikowego do importu oraz raportu pomocniczego.

## Struktura projektu

```text
horpach-benzara/
  config/
  data/
    inbox/
    working/
    output/
  docs/
  src/
    horpach_benzara/
      loaders/
      normalizers/
      matchers/
      rules/
      exporters/
  tests/
```

## Najwazniejsze decyzje do doprecyzowania

- finalny format pliku `d` - CSV czy XML
- wzor liczenia ceny sprzedazy
- progi kwalifikacji wysylki
- zasady publikacji nowych produktow

## Status

Aktualnie przygotowany jest szkielet projektu i dokumentacja startowa.

## MVP CLI

Program posiada pierwsza wersje CLI, ktora:

- wczytuje WooCommerce XML
- wczytuje katalog Benzara z XLSX
- wczytuje inventory XML
- laczy rekordy po SKU
- wykrywa WooCommerce SKU z pola `_sku`
- stosuje podstawowe filtry wysylkowe
- generuje wynikowy CSV z decyzjami `create`, `update`, `skip`

Uruchomienie:

```bash
python -m horpach_benzara.main ^
  --woo-xml data/inbox/horpachcom.WordPress.2026-06-24.xml ^
  --supplier-xlsx "data/inbox/FTP Benzara JUNE (15-06-2026).xlsx" ^
  --inventory-xml data/inbox/latest.xml ^
  --config config/config.example.json ^
  --output data/output/decisions.csv
```

Plik wynikowy `decisions.csv` jest roboczym eksportem do dalszego mapowania pod finalny format importu WooCommerce.

## Filtrowanie logistyczne Benzara

Drugi lokalny program filtruje sam katalog Benzara przed importem do WooCommerce i nie dotyka API sklepu.

Krotka struktura:

- `src/horpach_benzara/filter_benzara.py` - CLI do uruchomienia programu
- `src/horpach_benzara/filtering/logistics.py` - logika filtrowania po wadze, wymiarach, liczbie paczek i typie wysylki
- `output/products_allowed.csv` - produkty dopuszczone
- `output/products_removed_logistics.csv` - produkty usuniete z powodow logistycznych

Ta wersja programu analizuje tylko pierwszy zestaw logistyczny:

- `Ship Weight 1`
- `Ship Length 1`
- `Ship Width 1`
- `Ship Height 1`

oraz usuwa z pliku dopuszczonych produktow nieuzywane kolumny:

- `Product Weight 2-5`
- `Product Length 2-5`
- `Product Width 2-5`
- `Product Height 2-5`
- `Ship Weight 2-7`
- `Ship Length 2-7`
- `Ship Width 2-7`
- `Ship Height 2-7`

Zasady twardego usuniecia:

- dowolna paczka ma wage `> 30 lb`
- dowolna paczka ma dlugosc `> 48 in`
- dowolna paczka ma szerokosc `> 24 in`
- dowolna paczka ma wysokosc `> 24 in`
- suma wymiarow paczki `> 84 in`
- `Number Of Boxes > 1`
- `Ship Type Small Package/LTL` zawiera `LTL`, `Freight` lub `Freight Quote`
- `Inventory Qty < 10`

Uruchomienie:

```bash
python -m horpach_benzara.filter_benzara --input "data/inbox/FTP Benzara JUNE (15-06-2026).xlsx" --output-dir output
```

Wymagane zaleznosci:

```bash
pip install -r requirements.txt
```

## Audyt obrazow nowych produktow

Program do audytu obrazow bierze jako wejscie:

- `output/products_allowed.csv`
- `data/inbox/horpachcom.WordPress.2026-06-24.xml`

Dzialanie:

- rozdziela produkty na nowe i istniejace po SKU
- dla nowych waliduje wszystkie pola `Image URL N`
- najpierw probuje oryginalny URL
- potem warianty rozszerzen w tym samym katalogu
- na koncu probuje odzyskac adres ze strony produktu na `benzara.com`
- dla istniejacych produktow generuje plik update bez kolumn obrazow

Wyjscia:

- `output/products_create_with_images.csv`
- `output/products_update_without_images.csv`
- `output/products_new_image_audit.csv`
- `output/products_new_manual_image_review.csv`

Uruchomienie:

```bash
python -m horpach_benzara.image_audit --input output/products_allowed.csv --woo-xml data/inbox/horpachcom.WordPress.2026-06-24.xml --output-dir output --cache-dir output/cache
```
