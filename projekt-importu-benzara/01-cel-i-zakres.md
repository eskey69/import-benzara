# Cel i Zakres

## Problem do rozwiazania

Obecny plugin WooCommerce potrafi importowac dane z URL do XML lub CSV, ale wymaga:

- stabilnego formatu danych,
- sensownego modelu produktow,
- przewidywalnej struktury wariantow,
- recznej konfiguracji mapowania.

Projektowana aplikacja ma przejac odpowiedzialnosc za przygotowanie danych tak, aby import byl:

- powtarzalny,
- przewidywalny,
- prosty do utrzymania,
- odporny na zmiany po stronie dostawcow.

## Cel glowny

Stworzyc aplikacje publikujaca gotowy feed dla pluginu `Dropshipping XML WooCommerce PRO`.

## Cele szczegolowe

- zdefiniowac jeden model kanoniczny danych produktowych,
- wspierac wielu dostawcow przez warstwe adapterow,
- generowac XML w kontrolowanym schemacie,
- udostepniac feed pod stalym adresem URL,
- walidowac dane jeszcze przed publikacja,
- minimalizowac reczne mapowanie w pluginie.

## Co wchodzi do zakresu MVP

- import danych od jednego lub kilku dostawcow do modelu wewnetrznego,
- normalizacja produktow prostych i zmiennych,
- walidacja danych,
- generowanie feedu XML,
- publikacja feedu pod URL,
- dokumentacja mapowania dla pluginu,
- logi i podstawowa historia publikacji.

## Co nie musi wejsc do MVP

- pelne GUI dla zaawansowanych regol cenowych,
- CSV jako glowny format eksportu,
- obsluga niestandardowych naglowkow auth po stronie pluginu,
- rozbudowane workflow akceptacji biznesowej,
- wieloetapowe approvale feedu.

## Efekt koncowy MVP

Po zakonczeniu MVP powinnismy miec:

- aplikacje generujaca poprawny feed XML,
- wzorcowa konfiguracje pluginu WooCommerce,
- zestaw walidacji blokujacych zle dane,
- gotowy fundament do dalszej rozbudowy.
