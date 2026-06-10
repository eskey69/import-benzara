# import-benzara

Lokalna aplikacja do przygotowania pliku wsadowego dla pluginu `Dropshipping Import Products for WooCommerce` na podstawie danych Benzara.

## Cel

Pierwszy etap projektu:

- pobrać katalog referencyjny Benzara z pliku `FTP Benzara MAY (15-05-2026).xlsx`,
- podmienić lub uzupełnić w nim stany magazynowe z pliku `Benzara Inventory_19_05_2023.csv`,
- wygenerować plik CSV gotowy do aktualizacji istniejących produktów w WooCommerce przez plugin WP Desk.

Drugi etap projektu:

- przygotować moduł do wykrywania i uzupełniania brakujących lub błędnych URL-i zdjęć.

## Status startowy

- katalog roboczy i lokalne repo Git zostały utworzone,
- archiwa referencyjne zostały rozpakowane do `_analysis/`,
- dokumentacja robocza znajduje się w katalogu `docs/`.

## Najważniejsze ustalenia

- stara aplikacja `import-app` generowała wynik na bazie pełnego katalogu Benzara i doklejała kolumnę `Qty`,
- stary przepływ dodatkowo normalizował cenę i podmieniał prefiks URL zdjęć,
- plugin WP Desk obsługuje import i aktualizację produktów z CSV/XML, mapowanie po SKU oraz tryb `update existing products only`,
- pliki wejściowe mają rozbieżne daty w nazwach: `19-05-2023` i `15-05-2026`,
- pokrycie SKU między aktualnym plikiem stanów i katalogiem referencyjnym jest obecnie niskie i wymaga weryfikacji biznesowej.

## Dokumentacja projektu

- [Plan działania](./docs/PLAN.md)
- [Analiza wejścia i ryzyk](./docs/ANALYSIS.md)
- [Notatki o pluginie](./docs/PLUGIN-NOTES.md)

## Pierwsza wersja CLI

Aktualna wersja projektu zawiera pierwszy generator pliku wsadowego:

Najpierw uruchom z katalogu projektu:

```bash
python -m pip install -e .
```

albo ustaw tymczasowo `PYTHONPATH=src`.

Przykład:

```bash
python -m import_benzara generate ^
  --inventory "C:\Users\skrupa\Documents\!_benzara\produkty\Benzara Inventory_19_05_2023.csv" ^
  --catalog "C:\Users\skrupa\Documents\!_benzara\produkty\FTP Benzara MAY (15-05-2026).xlsx" ^
  --output "C:\Users\skrupa\Documents\import-benzara\data\output\benzara-update.csv"
```

Generator:

- łączy dane po `SKU`,
- zachowuje kolejność i strukturę kolumn z pliku katalogowego,
- aktualizuje kolumnę `Inventory Qty`, jeśli istnieje,
- zawsze dopisuje kolumnę `Qty`,
- generuje dodatkowe raporty `inventory-only`, `catalog-only` i `summary.json`.

## Założenia wersji v1

- eksportowane są tylko SKU obecne w obu plikach,
- nie tworzymy nowych produktów,
- nie modyfikujemy jeszcze URL-i zdjęć,
- raportujemy rozjazdy między źródłami zamiast ukrywać je w tle.
