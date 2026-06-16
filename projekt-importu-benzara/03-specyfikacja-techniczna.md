# Specyfikacja Techniczna

## Glowna zasada techniczna

Plugin WooCommerce finalnie pracuje na XML i XPath-ach. Dlatego aplikacja powinna traktowac XML jako podstawowy kontrakt eksportowy.

## Rekomendowana architektura

### 1. Adaptery dostawcow

Warstwa odpowiedzialna za pobranie i wstepne parsowanie danych zrodlowych.

Wejscie:

- pliki,
- API,
- feedy partnerow,
- inne zrodla uzgodnione biznesowo.

Wyjscie:

- rekordy w formacie surowym dostawcy.

### 2. Warstwa normalizacji

Warstwa odpowiedzialna za mapowanie danych dostawcy do modelu kanonicznego.

Powinna rozdzielac:

- pola produktu glownego,
- pola wariantu,
- dane wspolne,
- dane opcjonalne,
- meta i integracje specjalne.

### 3. Warstwa walidacji

Powinna obejmowac:

- walidacje techniczna,
- walidacje biznesowa,
- walidacje relacji parent-child,
- walidacje unikalnosci.

### 4. Eksporter XML

Powinien generowac:

- poprawny XML UTF-8,
- stabilna kolejnosc pol,
- powtarzalna strukture,
- bezpieczne CDATA dla opisow HTML.

### 5. Publisher feedu

Powinien:

- zapisywac feed w stabilnej lokalizacji,
- udostepniac go po HTTP(S),
- pilnowac aby URL nie zmienial sie przy zwyklych aktualizacjach.

### 6. Warstwa administracyjna

Powinna umozliwiac:

- uruchomienie importu danych do aplikacji,
- przeglad bledow,
- publikacje feedu,
- podglad przykladowego XML.

## Wymagania niefunkcjonalne

### Deterministycznosc

Te same dane wejsciowe powinny generowac ten sam feed.

### Diagnostyka

Kazdy blad powinien byc przypisany do:

- dostawcy,
- produktu,
- wariantu,
- pola lub etapu przetwarzania.

### Stabilnosc kontraktu

Struktura feedu nie powinna zmieniac sie bez potrzeby, bo wymusza to zmiany w konfiguracji pluginu.

### Wydajnosc

Aplikacja powinna byc gotowa do pracy na pelnych feedach, a nie tylko na testowych probkach.

### Odtwarzalnosc

Powinnismy umiec odtworzyc:

- jaka wersja danych weszla,
- jaki feed wyszedl,
- jakie rekordy odpadly i dlaczego.

## Preferowana strategia wdrozeniowa

- najpierw eksport statyczny i reczne testy,
- potem automatyzacja publikacji,
- na koncu pelny harmonogram i monitoring.
