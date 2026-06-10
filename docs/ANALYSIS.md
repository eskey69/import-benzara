# Analiza wejścia i ryzyk

## Pliki wejściowe

1. `woocommerce-dropshipping-xml.zip`
   Baza funkcjonalna pluginu WordPress odpowiedzialnego za import i synchronizację produktów.
2. `import-app.zip`
   Stara aplikacja pomocnicza do generowania pliku wsadowego dla pluginu.
3. `Benzara Inventory_19_05_2023.csv`
   Plik stanów magazynowych w układzie `SKU`, `Qty`.
4. `FTP Benzara MAY (15-05-2026).xlsx`
   Plik katalogowy z danymi referencyjnymi produktu, cenami, wymiarami i URL-ami zdjęć.

## Ustalenia techniczne

### Stara aplikacja

Stara aplikacja działała według prostego schematu:

1. wczytywała pełny katalog produktów,
2. wczytywała plik stanów `SKU` + `Qty`,
3. brała tylko produkty istniejące w obu plikach,
4. filtrowała produkty z `Qty > 5`,
5. normalizowała cenę,
6. zamieniała prefiks historycznych URL-i zdjęć,
7. dopisywała kolumnę `Qty`,
8. eksportowała finalny CSV.

### Obecne dane

- plik stanów ma 18 032 wiersze,
- plik stanów ma 17 994 unikalne SKU,
- plik katalogowy ma 14 758 wierszy i 14 758 unikalnych SKU,
- część wspólna obu zbiorów to 3 375 SKU,
- 11 383 SKU z katalogu nie występuje w pliku stanów,
- w pliku stanów nie znaleziono pustych ani nienumerycznych wartości `Qty`.

### Zgodność nagłówków

- historyczny wynik starej aplikacji odpowiadał strukturze katalogu referencyjnego plus kolumna `Qty`,
- w starszym pliku widoczna jest kolumna ` Wholesale Price ` ze spacjami,
- w aktualnym arkuszu kolumna nazywa się `Wholesale Price` bez spacji,
- to oznacza, że nowa aplikacja nie może polegać na dosłownym dopasowaniu starego nagłówka.

## Ryzyka do obsłużenia

### Ryzyko 1: rozjazd dat źródeł

Nazwy plików sugerują różne okresy:

- `Benzara Inventory_19_05_2023.csv`
- `FTP Benzara MAY (15-05-2026).xlsx`

To nie musi oznaczać błędnych danych, ale przy tak niskim pokryciu SKU jest to pierwsza rzecz do potwierdzenia przed wdrożeniem automatu produkcyjnego.

### Ryzyko 2: niski overlap SKU

Jeżeli rzeczywiście aktualizacja ma obejmować istniejącą bazę produktów na serwerze, trzeba ustalić:

- czy serwerowa baza była budowana z innego snapshotu katalogu,
- czy `Inventory` zawiera tylko wycinek produktów,
- czy część SKU została zmieniona po stronie Benzara,
- czy docelowy import ma aktualizować tylko część katalogu.

### Ryzyko 3: niejasna reguła biznesowa dla brakujących SKU

Musimy podjąć decyzję dla SKU:

- obecnych w katalogu, ale nieobecnych w pliku stanów,
- obecnych w pliku stanów, ale nieobecnych w katalogu.

Domyślna, bezpieczna strategia dla pierwszej wersji:

- generować wynik wyłącznie dla SKU wspólnych,
- nie tworzyć nowych produktów,
- nie nadpisywać danych, których nie umiemy wiarygodnie odtworzyć.
