# Specyfikacja Funkcjonalna

## Glowny workflow

1. Aplikacja pobiera dane od dostawcy.
2. Dane sa mapowane do modelu kanonicznego.
3. Rekordy przechodza walidacje biznesowa i techniczna.
4. Aplikacja generuje feed XML.
5. Feed jest publikowany pod stalym URL.
6. Operator konfiguruje plugin WooCommerce raz lub aktualizuje go tylko przy zmianach struktury.
7. WooCommerce wykonuje cykliczny import po URL.

## Role

### Operator integracji

Odpowiada za:

- dodanie nowego zrodla dostawcy,
- sprawdzenie wynikow walidacji,
- publikacje feedu,
- utrzymanie mapowania i konfiguracji importu.

### Administrator sklepu

Odpowiada za:

- konfiguracje pluginu WooCommerce,
- ustawienie harmonogramu importu,
- decyzje biznesowe dotyczace brakujacych produktow,
- nadzor nad finalnym katalogiem sklepu.

## Wymagania funkcjonalne

### Zrodla danych

Aplikacja powinna:

- przyjmowac dane z co najmniej jednego typu zrodla,
- pozwalac utrzymywac osobne profile dostawcow,
- przechowywac konfiguracje mapowania zrodla do modelu kanonicznego.

### Normalizacja danych

Aplikacja powinna:

- laczyc rozne formaty dostawcow do jednego modelu produktu,
- rozrozniac produkt prosty, zmienny i zewnetrzny,
- wspierac obrazy, kategorie, tagi, atrybuty i meta.

### Walidacja

Aplikacja powinna:

- odrzucac rekordy bez stabilnego identyfikatora,
- wykrywac duplikaty SKU i duplikaty kombinacji wariantow,
- sprawdzac ceny, stany, URL-e i poprawnosc XML,
- raportowac bledy w sposob czytelny dla operatora.

### Publikacja feedu

Aplikacja powinna:

- publikowac aktualny feed pod stalym URL,
- zachowywac przewidywalna strukture XML,
- opcjonalnie przechowywac poprzednie wersje feedow.

### Obsluga produktow zmiennych

Aplikacja powinna:

- grupowac warianty pod produktem glownym,
- generowac atrybuty wariantowe,
- zapewniac unikalnosc wariacji,
- wspierac obrazy, cene i stock na poziomie wariantu.

### Obsluga usunietych produktow

Aplikacja powinna umozliwic dwa style pracy:

- feed pelny, gdzie brak produktu w feedzie znaczy brak produktu w ofercie,
- feed tylko do aktualizacji, bez czyszczenia brakow po stronie pluginu.

## Wymagania raportowe

Aplikacja powinna pokazywac:

- liczbe rekordow wejscia,
- liczbe rekordow poprawnych,
- liczbe rekordow odrzuconych,
- liste bledow i ostrzezen,
- czas publikacji feedu,
- identyfikator lub timestamp wersji feedu.

## Wymagania dla konfiguracji pluginu

Aplikacja powinna dostarczyc operatorowi:

- rekomendowany URL feedu,
- wskazanie wezla produktu,
- zestaw sugerowanych XPath-ow,
- rekomendowany klucz synchronizacji,
- rekomendowane ustawienia dla brakujacych produktow.
