# Projekt Importu Benzara

Ten katalog jest glownym zbiorem materialow do projektu aplikacji, ktora ma przygotowywac i publikowac pliki importu dla pluginu `Dropshipping XML WooCommerce PRO`.

## Cel

Zbudowac aplikacje, ktora:

- zbiera dane od dostawcow,
- normalizuje je do jednego modelu,
- generuje stabilny feed importowy,
- publikuje feed pod URL,
- upraszcza konfiguracje importu w WooCommerce.

## Najwazniejsze decyzje na tym etapie

- Format docelowy: XML.
- Model synchronizacji: `custom_product_id` albo `SKU`.
- Feed ma byc stale dostepny po HTTP(S).
- Rekord produktu powinien byc reprezentowany przez jeden powtarzalny wezel `product`.
- Wariacje najlepiej eksportowac jako dzieci produktu w XML.

## Zawartosc katalogu

- [01-cel-i-zakres.md](C:/Users/skrupa/Documents/Benzara%20project/projekt-importu-benzara/01-cel-i-zakres.md)
- [02-specyfikacja-funkcjonalna.md](C:/Users/skrupa/Documents/Benzara%20project/projekt-importu-benzara/02-specyfikacja-funkcjonalna.md)
- [03-specyfikacja-techniczna.md](C:/Users/skrupa/Documents/Benzara%20project/projekt-importu-benzara/03-specyfikacja-techniczna.md)
- [04-model-danych.md](C:/Users/skrupa/Documents/Benzara%20project/projekt-importu-benzara/04-model-danych.md)
- [05-struktura-feedu-xml.md](C:/Users/skrupa/Documents/Benzara%20project/projekt-importu-benzara/05-struktura-feedu-xml.md)
- [06-ryzyka-i-zalozenia.md](C:/Users/skrupa/Documents/Benzara%20project/projekt-importu-benzara/06-ryzyka-i-zalozenia.md)
- [07-plan-realizacji.md](C:/Users/skrupa/Documents/Benzara%20project/projekt-importu-benzara/07-plan-realizacji.md)
- [08-otwarte-pytania.md](C:/Users/skrupa/Documents/Benzara%20project/projekt-importu-benzara/08-otwarte-pytania.md)
- [09-specyfikacja-zrodel-benzara.md](C:/Users/skrupa/Documents/Benzara%20project/projekt-importu-benzara/09-specyfikacja-zrodel-benzara.md)
- [10-specyfikacja-importu-stock-benzara.md](C:/Users/skrupa/Documents/Benzara%20project/projekt-importu-benzara/10-specyfikacja-importu-stock-benzara.md)

## Materialy referencyjne

- [reference/analiza-pluginu.md](C:/Users/skrupa/Documents/Benzara%20project/projekt-importu-benzara/reference/analiza-pluginu.md)
- [reference/recommended-dropshipping-feed.xml](C:/Users/skrupa/Documents/Benzara%20project/projekt-importu-benzara/reference/recommended-dropshipping-feed.xml)

## Jak czytac ten pakiet

1. Zacznij od celu i zakresu.
2. Przejdz do specyfikacji funkcjonalnej i technicznej.
3. Potem sprawdz model danych i format feedu.
4. Na koncu przejdz przez ryzyka, plan i otwarte pytania.

## Aktualny stan

Ten pakiet jest punktem startowym do:

- projektowania architektury aplikacji,
- przygotowania backlogu MVP,
- ustalenia finalnego modelu danych,
- pozniejszego wdrozenia eksportu XML i publikacji feedu.
