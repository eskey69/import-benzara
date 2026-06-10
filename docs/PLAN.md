# Plan działania

## Cel etapu 1

Zbudować aplikację `import-benzara`, która z dwóch plików wejściowych wygeneruje stabilny plik CSV do aktualizacji istniejących produktów WooCommerce przez `Dropshipping Import Products for WooCommerce`.

## Rekomendowana architektura

Rekomenduję aplikację lokalną w Pythonie z interfejsem CLI.

Powody:

- bezproblemowa obsługa `xlsx` i `csv`,
- szybka walidacja dużych zbiorów danych,
- łatwe raportowanie różnic i błędów,
- dobre podstawy pod drugi etap projektu, czyli weryfikację zdjęć i URL-i.

Proponowany układ katalogów:

- `src/import_benzara/`
- `tests/`
- `docs/`
- `data/input/`
- `data/output/`
- `tmp/`

## Etapy implementacji

### Etap 0: ustalenia wejścia i reguł biznesowych

Do potwierdzenia przed pierwszym importem produkcyjnym:

1. Czy plik `Benzara Inventory_19_05_2023.csv` jest faktycznie aktualnym źródłem stanów mimo daty w nazwie.
2. Czy wynik ma obejmować tylko SKU wspólne dla obu plików.
3. Czy dla SKU bez wpisu w `Inventory` ustawiamy `0`, pomijamy je, czy zostawiamy bez zmiany.
4. Czy zachowujemy historyczny filtr `Qty > 5`, czy aktualizujemy wszystkie ilości.
5. Czy w etapie 1 aktualizujemy wyłącznie stan, czy również ceny i zdjęcia.

Domyślna propozycja dla wersji `v1`:

- aktualizować tylko istniejące produkty,
- identyfikować po `SKU`,
- generować wiersze tylko dla SKU wspólnych,
- nie tworzyć nowych produktów,
- nie modyfikować zdjęć w etapie 1,
- nie wprowadzać filtra `Qty > 5`, chyba że potwierdzisz jego dalszą potrzebę.

### Etap 1: scaffold aplikacji

Zakres:

1. utworzyć pakiet Python,
2. dodać CLI, np. `python -m import_benzara`,
3. dodać plik konfiguracyjny z mapowaniem kolumn i regułami biznesowymi,
4. przygotować katalog na raporty i eksporty.

Rezultat:

- powtarzalny punkt wejścia do generowania importu,
- brak ręcznych zmian w kodzie przy każdej nowej dostawie plików.

### Etap 2: warstwa wejścia danych

Zakres:

1. loader `Inventory CSV`,
2. loader `FTP XLSX`,
3. normalizacja nazw kolumn,
4. normalizacja `SKU`,
5. walidacja typów i braków danych.

Rezultat:

- wewnętrzny, jednolity model danych niezależny od różnic formatowania wejścia.

### Etap 3: silnik łączenia i transformacji

Zakres:

1. join po `SKU`,
2. obsługa duplikatów SKU,
3. polityka dla brakujących rekordów,
4. generowanie końcowej struktury kolumn,
5. opcjonalna normalizacja ceny,
6. opcjonalna podmiana prefiksu URL zdjęć jako osobna reguła, wyłączona domyślnie.

Rezultat:

- deterministyczny dataset wyjściowy gotowy do eksportu.

### Etap 4: eksport do pliku wsadowego

Zakres:

1. zapis finalnego `CSV`,
2. zapis raportu `summary.json` lub `summary.csv`,
3. zapis listy braków:
   - SKU tylko w `Inventory`,
   - SKU tylko w katalogu,
   - duplikaty,
   - rekordy odrzucone.

Rezultat:

- plik do importu oraz raport kontrolny do weryfikacji przed użyciem na serwerze.

### Etap 5: testy

Zakres:

1. testy jednostkowe normalizacji i mapowania,
2. test próbki integracyjnej na małym zestawie SKU,
3. porównanie struktury wyniku z oczekiwanym formatem pluginu,
4. suchy bieg na pełnych plikach wejściowych.

Rezultat:

- możliwość bezpiecznego powtarzania importu przy nowych plikach Benzara.

### Etap 6: test operacyjny z pluginem WP Desk

Zakres:

1. skonfigurować import po `SKU`,
2. włączyć `update existing products only`,
3. ograniczyć zakres aktualizacji do ustalonych pól,
4. wykonać import na małej próbce,
5. sprawdzić log pluginu i efekt w WooCommerce.

Rezultat:

- potwierdzenie, że plik działa poprawnie na realnym środowisku.

## Etap 2 projektu: moduł zdjęć

Ten etap zaczniemy dopiero po zamknięciu etapu 1.

Plan wysokopoziomowy:

1. zidentyfikować błędne URL-e zdjęć,
2. zbudować walidator dostępności obrazów,
3. przygotować mechanizm wyszukiwania alternatywnych URL-i,
4. zbudować kolejkę do ręcznej weryfikacji przypadków nierozstrzygalnych,
5. opcjonalnie generować poprawiony feed zdjęć do ponownego importu.

## Kryteria akceptacji etapu 1

Etap 1 uznajemy za gotowy, gdy:

1. aplikacja przyjmuje dwa pliki wejściowe bez ręcznej edycji,
2. generuje finalny CSV do pluginu WP Desk,
3. raportuje różnice i błędy danych,
4. przechodzi test na próbce,
5. przechodzi test na pełnych danych,
6. aktualizacja na serwerze działa dla wybranej próbki produktów.

## Najbliższy proponowany krok

Następny krok w Codexie:

1. zatwierdzić reguły biznesowe z sekcji `Etap 0`,
2. zbudować skeleton aplikacji Python,
3. dodać loader wejścia i pierwszy eksport próbki CSV,
4. przygotować testową paczkę kilkunastu SKU do walidacji w WooCommerce.
