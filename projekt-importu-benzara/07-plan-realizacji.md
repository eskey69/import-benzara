# Plan Realizacji

## Etap 1. Domkniecie decyzji projektowych

- wybrac finalny model danych,
- potwierdzic klucz synchronizacji,
- ustalic format i hosting feedu,
- potwierdzic zakres MVP.

## Etap 2. Fundament techniczny

- przygotowac strukture projektu aplikacji,
- dodac warstwe adapterow dostawcow,
- dodac model kanoniczny,
- dodac walidatory.

## Etap 3. Eksport feedu

- zaimplementowac generator XML,
- dodac feed przykładowy i testowy,
- zapewnic stabilny URL publikacji,
- dodac wersjonowanie lub przynajmniej timestamp publikacji.

## Etap 4. Integracja z WooCommerce

- skonfigurowac plugin na feed testowy,
- sprawdzic import produktow prostych,
- sprawdzic import produktow zmiennych,
- sprawdzic obrazy, kategorie i atrybuty,
- sprawdzic zachowanie przy brakujacym produkcie.

## Etap 5. Twarde testy

- duze feedy,
- duplikaty SKU,
- brakujace obrazy,
- niepoprawne ceny,
- nietypowe znaki,
- problemy wariantow.

## Etap 6. Produkcja

- harmonogram odswiezania danych,
- monitoring publikacji feedu,
- monitoring wynikow importu,
- procedury rollbacku i diagnozy.

## Proponowany backlog MVP

1. Model `Product` i `Variation`
2. Adapter jednego dostawcy
3. Walidacja danych
4. Eksporter XML
5. Publikacja feedu
6. Raport bledow
7. Instrukcja mapowania dla pluginu
8. Test end-to-end z WooCommerce

## Definicja sukcesu MVP

MVP jest gotowe, gdy:

- generujemy poprawny XML,
- plugin importuje go bez recznych obejsc,
- produkty proste i zmienne aktualizuja sie stabilnie,
- operator widzi, ktore rekordy odpadly i dlaczego.
