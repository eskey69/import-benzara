# Specyfikacja Zrodel Danych Benzara

## Cel dokumentu

Ten dokument opisuje rzeczywista strukture i zasady przetwarzania dwoch glowych zrodel danych Benzara:

- pelnego pliku bazowego z katalogiem produktow,
- cyklicznego pliku inventory do aktualizacji stanow magazynowych.

Dokument jest podstawa do implementacji importera, normalizacji danych i generatora feedu dla WooCommerce.

## Przeanalizowane pliki

- `FTP Benzara MAY (15-05-2026).xlsx`
- `Benzara Inventory_19_05_2023.csv`
- `benzara_Inventory_15_06_2026.csv`

## Wnioski wysokiego poziomu

- `FTP Benzara MAY (15-05-2026).xlsx` jest plikiem bazowym z pelnym katalogiem.
- Pliki inventory maja prosty format `SKU,Qty` i sluza do nadpisywania stanow magazynowych.
- Najbezpieczniejszym kluczem laczenia jest `SKU`.
- `UPC` nie nadaje sie na glowny klucz synchronizacji, bo ma braki i duplikaty.
- Dane bazowe wymagaja normalizacji tekstowej przed eksportem.
- Biezacy inventory nie pokrywa sie idealnie z baza, wiec aplikacja musi obsluzyc rozjazdy danych.

## 1. Plik bazowy XLSX

### 1.1. Struktura

- liczba arkuszy: `1`
- nazwa arkusza: `Sheet1`
- liczba rekordow: `14758`
- liczba kolumn: `97`
- klucz unikalny: `SKU`

### 1.2. Najwazniejsze pola

#### Identyfikacja

- `SKU`
- `UPC`
- `Brand`
- `Year Cataloged`

#### Tresci i prezentacja

- `Title`
- `Description`
- `Bullet 1` ... `Bullet 5`
- `Material`
- `Finish`
- `Color`
- `Attribute 1` ... `Attribute 5`

#### Cena i stock

- `Wholesale Price`
- `Inventory Qty`

#### Wymiary produktu

- `Product Weight 1` ... `Product Weight 5`
- `Product Length 1` ... `Product Height 5`
- `ProductDimensionsUnit`
- `ProductWeightUnit`

#### Wymiary wysylkowe

- `Ship Weight 1` ... `Ship Weight 7`
- `Ship Length 1` ... `Ship Height 7`
- `ShippingDimensionsUnit`
- `ShippingWeightUnit`
- `DIM1` ... `DIM4`
- `Number Of Boxes`
- `Ship Type Small Package/LTL`
- `Shiping Information`

#### Klasyfikacja i pochodzenie

- `Category`
- `Origin`
- `Assembly Needed`

#### Media

- `Image URL 1` ... `Image URL 11`

#### Compliance

- `Prop65 Warning`
- `Chemical Info`
- `Type of Toxicity`

### 1.3. Jak interpretowac plik bazowy

- jeden wiersz opisuje jeden produkt,
- `SKU` jest unikalne w calej probce,
- plik wyglada na katalog produktow prostych, nie na feed wariantowy,
- `Inventory Qty` w pliku bazowym jest stanem startowym, ale nie powinno byc traktowane jako finalny stock po pojawieniu sie nowszego pliku inventory.

## 2. Pliki inventory CSV

### 2.1. Struktura

Oba przeanalizowane pliki inventory maja identyczny, bardzo prosty schemat:

- `SKU`
- `Qty`

Separator:

- przecinek `,`

### 2.2. Rola biznesowa

Plik inventory nie niesie opisu produktu, ceny, kategorii ani obrazow. Jego zadaniem jest jedynie aktualizacja stanow magazynowych po `SKU`.

### 2.3. Wzorzec nazewnictwa

W praktyce trzeba wspierac co najmniej warianty:

- `Benzara Inventory_DD_MM_RRRR.csv`
- `benzara_Inventory_DD_MM_RRRR.csv`

Wniosek implementacyjny:

- parser nazwy pliku powinien byc niewrazliwy na wielkosc liter,
- data z nazwy pliku powinna byc zapisywana jako `inventory_snapshot_date`.

## 3. Jak laczyc baze z inventory

### 3.1. Klucz laczenia

Podstawowy klucz:

- `SKU`

Nie rekomenduje sie laczenia po:

- `Title`
- `UPC`

Powody:

- `Title` nie jest stabilnym identyfikatorem,
- `UPC` ma `907` brakow i co najmniej jeden duplikat wielokrotny.

### 3.2. Fakty wykryte w aktualnych plikach

- baza: `14758` SKU
- inventory `15_06_2026`: `14509` unikalnych SKU
- rekordow wspolnych: `14279`
- SKU z inventory nieobecne w bazie: `230`
- SKU z bazy nieobecne w inventory: `479`
- zduplikowane SKU w inventory: `14`
- konfliktowych duplikatow w inventory: `0`

### 3.3. Znaczenie tych roznic

Rozjazd miedzy baza i inventory oznacza, ze:

- baza nie jest w pelni zgodna z najnowszym snapshotem stocku,
- inventory moze zawierac SKU nowsze niz aktualny plik bazowy,
- sama aktualizacja stocku musi miec jawne reguly obslugi brakow.

## 4. Rekomendowany algorytm laczenia

### 4.1. Zasada ogolna

1. Wczytaj najnowszy plik bazowy.
2. Wczytaj najnowszy plik inventory.
3. Oczysc i znormalizuj `SKU` po obu stronach.
4. Zdeduplikuj inventory po `SKU`.
5. Dla zgodnych `SKU` nadpisz `Inventory Qty` wartoscia `Qty`.
6. Zaloguj rekordy niezgodne i podejmij decyzje zgodnie z polityka biznesowa.

### 4.2. Dedup inventory

Poniewaz wykryte duplikaty w inventory nie maja konfliktowych wartosci `Qty`, aplikacja moze:

- zachowac ostatni rekord,
- albo zwinac duplikaty do jednego wpisu po walidacji, ze wszystkie `Qty` sa identyczne.

Jesli w przyszlosci pojawia sie konfliktowe duplikaty:

- import inventory powinien zostac oznaczony jako blad walidacji,
- feed nie powinien byc publikowany automatycznie bez decyzji operatora.

### 4.3. SKU obecne w inventory, ale nieobecne w bazie

Rekomendowane zachowanie:

- nie publikowac ich do feedu z samego inventory,
- logowac je jako `inventory_only_sku`,
- traktowac jako sygnal, ze potrzebne jest odswiezenie pliku bazowego.

### 4.4. SKU obecne w bazie, ale nieobecne w inventory

To jest decyzja biznesowa, ale rekomendowany domyslny tryb dla sklepu jest taki:

- ustawic `stock_qty = 0`,
- ustawic `stock_status = outofstock`,
- zachowac rekord produktu w feedzie,
- dodatkowo oznaczyc rekord flaga `missing_in_inventory_snapshot = true`.

Alternatywny tryb, jesli biznes potwierdzi inna semantyke:

- zachowac ostatni znany stock zamiast zerowania.

## 5. Normalizacja danych bazowych

### 5.1. Pola tekstowe z wartoscia `0`

W wielu kolumnach tekstowych `0` oznacza w praktyce brak wartosci, a nie literalna wartosc biznesowa.

Dotyczy to w szczegolnosci:

- `Finish`
- `Attribute 1` ... `Attribute 5`
- `Bullet 4`
- `Bullet 5`
- `Category`
- `Origin`
- `Year Cataloged`
- `Chemical Info`

Regula:

- string `0` po trimie powinien byc zamieniany na `null`, chyba ze dla konkretnego pola ustalimy inna semantyke.

### 5.2. Normalizacja brandu

W bazie wystepuja warianty zapisu brandu, m.in.:

- `Benjara`
- `Benzara`
- `benjara`
- `BENZARA`
- `BenJara`

Regula:

- przechowywac `brand_raw`,
- wyliczac `brand_normalized`,
- stosowac slownik normalizacji.

### 5.3. Normalizacja kategorii

Pole `Category` nie ma jednego spojnego formatu. Wystepuja:

- wartosci pojedyncze,
- drzewa z separatorem `>`,
- warianty z dodatkowymi spacjami,
- wartosci `0`,
- prawdopodobne literowki i niespojnosci stylu.

Reguly:

- usunac zbedne spacje wokol separatora `>`,
- zamienic wielokrotne warianty zapisu na jeden kanoniczny format,
- potraktowac `0` jako brak kategorii,
- zachowac `category_raw`,
- wyliczac `category_path_normalized`.

## 6. Mapowanie do modelu kanonicznego aplikacji

### 6.1. Pola podstawowe

- `custom_product_id` -> `SKU`
- `sku` -> `SKU`
- `ean` -> `UPC` jako string, jesli niepuste
- `name` -> `Title`
- `description_html` -> `Description`
- `short_description_html` -> generowane z `Bullet 1` ... `Bullet 5` albo z dedykowanej reguly skrotu
- `regular_price` -> `Wholesale Price`
- `stock_qty` -> `Inventory Qty` zaktualizowane przez `Qty` z inventory
- `stock_status` -> wyliczane z `stock_qty`
- `brand` -> `brand_normalized`
- `origin` -> `Origin`

### 6.2. Atrybuty

Rekomendowane stale atrybuty:

- `Material` -> atrybut `Material`
- `Finish` -> atrybut `Finish`
- `Color` -> atrybut `Color`

Pola `Attribute 1` ... `Attribute 5` powinny byc parsowane regula:

- jesli wartosc ma postac `Nazwa : Wartosc`, rozdzielic do pary atrybutowej,
- jesli nie ma separatora `:`, zachowac jako tekst pomocniczy lub meta,
- puste wartosci i `0` ignorowac.

### 6.3. Obrazy

Regula:

- zebrac wszystkie niepuste URL z pol `Image URL 1` ... `Image URL 11`,
- zachowac kolejnosc,
- odrzucic wartosci puste i `0`.

Stan aktualnej probki:

- `Image URL 1` ... `Image URL 7` sa wypelnione we wszystkich rekordach,
- `Image URL 8` ... `Image URL 11` sa puste w calej probce.

### 6.4. Wymiary

Dla WooCommerce i feedu importowego rekomenduje sie:

- glowna waga i wymiary produktu z zestawu `Product Weight 1`, `Product Length 1`, `Product Width 1`, `Product Height 1`,
- dodatkowe wymiary paczek przechowywac jako meta pomocnicze,
- `Number Of Boxes` zachowac jako meta,
- shipping box data zachowac jako meta lub dane logistyczne poza glownym feedem.

Powod:

- plugin WooCommerce obsluguje jeden podstawowy zestaw wymiarow produktu,
- zrodlo Benzara ma dane wielopaczkowe, ktorych nie da sie bezstratnie odwzorowac w jednym prostym modelu Woo.

## 7. Reguly walidacji

### 7.1. Walidacje pliku bazowego

- `SKU` musi byc niepuste i unikalne,
- `Title` musi byc niepuste,
- `Description` musi byc niepuste,
- `Wholesale Price` musi byc liczba dodatnia,
- `Inventory Qty` musi byc liczba calkowita `>= 0`.

### 7.2. Walidacje inventory

- plik musi miec kolumny `SKU`, `Qty`,
- `SKU` nie moze byc puste,
- `Qty` musi byc liczba calkowita `>= 0`,
- duplikaty SKU sa dozwolone tylko wtedy, gdy wszystkie maja identyczne `Qty`,
- konfliktowe duplikaty powinny blokowac publikacje.

### 7.3. Walidacje po laczeniu

- raport liczby SKU wspolnych, tylko-baza, tylko-inventory,
- raport zmian stocku wzgledem pliku bazowego,
- raport SKU, dla ktorych brakuje aktualnego inventory,
- raport SKU nowych, wymagajacych odswiezenia bazy.

## 8. Rekomendacja architektoniczna

Najbezpieczniejszy model pracy aplikacji jest dwuetapowy:

1. Pelny refresh katalogu z XLSX wykonywany okresowo.
2. Czeste odswiezanie stocku z najnowszego pliku inventory wykonywane po `SKU`.

To oznacza, ze aplikacja powinna przechowywac:

- `catalog_snapshot_date`
- `inventory_snapshot_date`
- `source_file_name_base`
- `source_file_name_inventory`
- wynik walidacji i liczbe odchylen.

## 9. Decyzje do zamkniecia

- czy brak SKU w inventory oznacza `0`, czy brak aktualizacji,
- jak czesto odswiezac plik bazowy,
- czy `Wholesale Price` ma byc cena eksportowana 1:1, czy baza do dalszej marzy,
- czy shipping box data ma trafic do meta w WooCommerce,
- czy produkty z inventory-only maja czekac na nowa baze, czy maja byc raportowane jako blad krytyczny.

## 10. Rekomendacja koncowa

Na podstawie analizy tych plikow rekomenduje:

- traktowac `SKU` jako jedyny stabilny klucz laczenia,
- traktowac XLSX jako zrodlo pelnych danych produktowych,
- traktowac najnowszy inventory CSV jako zrodlo prawdy dla stocku,
- normalizowac `brand`, `category` i tekstowe `0`,
- nie opierac synchronizacji na `UPC`,
- wdrozyc jawne raportowanie rozjazdow miedzy katalogiem i inventory.
