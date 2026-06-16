# Specyfikacja Importu Stocku Benzara

## Cel dokumentu

Ten dokument definiuje logike aplikacji przygotowujacej plik importowy dla modulu `Dropshipping XML WooCommerce PRO` w scenariuszu aktualizacji stanow magazynowych Benzara.

Zakres tego dokumentu dotyczy tylko logiki stocku, a nie pelnego importu opisow, cen, kategorii i obrazow.

## Zasada biznesowa

Importujemy do sklepu tylko realne stany magazynowe od `10` sztuk wzwyz.

Regula docelowa:

- jesli `Qty >= 10`, importowany stan magazynowy jest rowny `Qty`
- jesli `Qty < 10`, importowany stan magazynowy jest ustawiany na `0`

To oznacza, ze stany `0` do `9` sa w sklepie traktowane tak samo:

- `stock_qty = 0`
- `stock_status = outofstock`

## Zrodla danych

### Plik bazowy

- `FTP Benzara MAY (15-05-2026).xlsx`

Rola:

- zrodlo pelnej listy produktow do feedu stockowego

Minimalnie wymagane pole:

- `SKU`

### Plik inventory

- `Benzara Inventory_*.csv`

Rola:

- zrodlo aktualnego stanu magazynowego

Wymagane pola:

- `SKU`
- `Qty`

## Klucz synchronizacji

Jedynym rekomendowanym kluczem laczenia i synchronizacji jest:

- `SKU`

Nie nalezy uzywac:

- `Title`
- `UPC`

## Cel eksportu do pluginu

Aplikacja ma generowac lekki XML przeznaczony do aktualizacji pol stockowych po `SKU`.

Feed nie musi zawierac calego opisu produktu, jesli import ma sluzyc tylko aktualizacji stanow.

## Algorytm aplikacji

### 1. Wczytanie danych

1. Wczytaj plik bazowy XLSX.
2. Znajdz najnowszy plik inventory CSV po dacie w nazwie.
3. Zweryfikuj, ze oba pliki zawieraja wymagane kolumny.

### 2. Normalizacja

Dla obu zrodel:

- przytnij spacje w `SKU`
- porownuj `SKU` bez wrazliwosci na wielkosc liter
- zachowaj oryginalne `SKU` z bazy jako wartosc eksportowa

### 3. Walidacja inventory

Plik inventory musi przejsc kontrole:

- `SKU` niepuste
- `Qty` jako liczba calkowita `>= 0`
- duplikaty `SKU` dozwolone tylko wtedy, gdy wszystkie rekordy maja identyczne `Qty`

Jesli pojawia sie konfliktowe duplikaty `SKU`:

- publikacja feedu powinna zostac zablokowana

### 4. Laczenie danych

Laczenie powinno byc wykonane jako:

- `left join` od bazy produktowej do inventory po `SKU`

To gwarantuje, ze:

- feed obejmuje cala baze produktow,
- produkty bez aktualnego wpisu inventory moga dostac kontrolowany stan `0`.

### 5. Wyliczenie stanu importowego

Dla kazdego produktu:

1. Odczytaj `Qty` z inventory.
2. Jesli `Qty >= 10`, ustaw `effective_qty = Qty`.
3. Jesli `Qty < 10`, ustaw `effective_qty = 0`.
4. Jesli produkt nie wystepuje w inventory, rekomendowane domyslne zachowanie to `effective_qty = 0`.

Formulacyjnie:

```text
effective_qty = Qty, gdy Qty >= 10
effective_qty = 0, gdy Qty < 10
effective_qty = 0, gdy brak SKU w inventory
```

### 6. Wyliczenie pol WooCommerce

Na podstawie `effective_qty`:

- `manage_stock = true`
- `stock_qty = effective_qty`
- `stock_status = instock`, gdy `effective_qty > 0`
- `stock_status = outofstock`, gdy `effective_qty = 0`

## Widocznosc produktow ze stanem 0

### Co robi plugin

W analizowanej wersji pluginu import ustawia `stock_status` na:

- `instock`, gdy stock jest dodatni
- `outofstock`, gdy stock jest rowny `0`

Plugin nie daje osobnej, dedykowanej logiki typu:

- `ukryj produkt, jesli stock = 0`

### Rekomendowany sposob ukrywania

Ukrywanie produktow ze stanem `0` powinno byc realizowane przez ustawienia WooCommerce, a nie przez pomijanie ich w feedzie.

Rekomendacja:

- importowac produkt z `stock_qty = 0`
- ustawic `stock_status = outofstock`
- wlaczyc w WooCommerce opcje ukrywania produktow niedostepnych w katalogu

### Dlaczego nie pomijac takich rekordow w feedzie

Jesli produkt z niskim stanem nie zostanie w ogole wyslany w feedzie:

- istnieje ryzyko, ze w sklepie pozostanie poprzedni dodatni stock,
- produkt moze pozostac sprzedawalny mimo spadku stanu ponizej progu.

Dlatego rekord powinien pozostac w feedzie, ale z wyzerowanym stockiem.

## Produkty nieobecne w inventory

Rekomendowana polityka dla produktow z bazy, ktore nie wystepuja w najnowszym inventory:

- `stock_qty = 0`
- `stock_status = outofstock`
- produkt pozostaje w feedzie
- rekord powinien trafic do raportu jako `missing_in_inventory`

To jest bezpieczniejszy tryb operacyjny niz zachowywanie starego stocku.

## Produkty obecne tylko w inventory

Jesli `SKU` wystepuje w inventory, ale nie ma go w bazie:

- nie eksportowac takiego rekordu do feedu stockowego
- dodac go do raportu jako `inventory_only_sku`
- potraktowac jako sygnal potrzeby odswiezenia pliku bazowego

## Struktura rekomendowanego XML

Minimalny feed stockowy moze miec taka forme:

```xml
<catalog>
  <products>
    <product>
      <sku>BM346842</sku>
      <stock>
        <manage>true</manage>
        <qty>46</qty>
        <status>instock</status>
      </stock>
    </product>
    <product>
      <sku>BM346824</sku>
      <stock>
        <manage>true</manage>
        <qty>0</qty>
        <status>outofstock</status>
      </stock>
    </product>
  </products>
</catalog>
```

## Konfiguracja pluginu

### Identyfikacja produktu

Plugin powinien laczyc produkty po:

- `SKU`

### Wezel produktu

- `catalog/products/product`

### Pola do mapowania

Minimalny zakres mapowania:

- `sku`
- `stock/qty`
- `stock/status`
- `stock/manage`

### Synchronizowane pola

W imporcie stockowym nalezy ograniczyc synchronizacje do pol magazynowych, tak aby nie nadpisywac:

- nazw
- opisow
- cen
- kategorii
- obrazow

## Walidacje przed publikacja

Przed wygenerowaniem feedu aplikacja powinna sprawdzic:

- czy baza zawiera unikalne `SKU`
- czy inventory ma poprawne `SKU`
- czy `Qty` jest liczba calkowita `>= 0`
- czy nie ma konfliktowych duplikatow `SKU` w inventory
- czy finalny XML jest poprawny

## Raport po przetworzeniu

Aplikacja powinna generowac raport zawierajacy co najmniej:

- liczbe rekordow w bazie
- liczbe rekordow w inventory
- liczbe rekordow wspolnych
- liczbe SKU tylko w bazie
- liczbe SKU tylko w inventory
- liczbe rekordow ustawionych jako `instock`
- liczbe rekordow ustawionych jako `outofstock`
- liczbe rekordow wyzerowanych przez prog `< 10`

## Rekomendacja operacyjna

Najbezpieczniejszy model pracy:

1. Pelny plik bazowy jest odswiezany okresowo.
2. Najnowszy inventory jest pobierany czesciej.
3. Feed stockowy jest publikowany po kazdym poprawnym przetworzeniu inventory.
4. Produkty z `Qty < 10` zawsze schodza do `0`.
5. Produkty `outofstock` sa ukrywane na froncie przez ustawienie WooCommerce.

## Decyzja koncowa

Docelowa logika aplikacji dla Benzara powinna byc taka:

- generuj feed dla calej bazy produktow,
- aktualizuj stock po `SKU`,
- importuj stan tylko od `10` sztuk wzwyz,
- wszystko ponizej `10` ustawiaj na `0`,
- nie pomijaj rekordow z niskim stockiem,
- ukrywaj je przez `outofstock` i konfiguracje WooCommerce, a nie przez brak wpisu w feedzie.
