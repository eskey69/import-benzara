# Namecheap Deployment

## Cel

Ten dokument opisuje rekomendowany sposob wdrozenia aplikacji `import-benzara` na hostingu Namecheap z obsluga aplikacji Python.

Model jest zgodny z mechanizmem `cPanel -> Setup Python App`, ktory wedlug dokumentacji Namecheap obsluguje aplikacje Python jako `WSGI app`, pozwala ustawic `Application startup file`, `Application Entry point`, zmienne srodowiskowe oraz instalacje zaleznosci przez `requirements.txt`.

## Model wdrozenia

Rekomendowany model:

- aplikacja Python jako `WSGI app`
- panel admin do uploadu plikow
- publiczny feed `feed.xml`
- cron do automatycznej regeneracji feedu

## Pliki wejciowe

Na serwer trafiaja dwa typy plikow:

- katalog `XLSX`
- inventory `CSV`

Panel zapisuje je do:

- `data/uploads/catalog/`
- `data/uploads/inventory/`

## Pliki wyjsciowe

Aktualny feed i raporty sa zapisywane do:

- `data/generated/latest/feed.xml`
- `data/generated/latest/feed.summary.json`
- `data/generated/latest/feed.inventory-only.csv`
- `data/generated/latest/feed.catalog-only.csv`

Historia przebiegow trafia do:

- `data/generated/runs/<run_id>/`

## Deployment krok po kroku

### 1. Wgraj projekt na serwer

Wgraj repozytorium do katalogu aplikacji, na przyklad:

- `/home/<user>/import-benzara`

### 2. Skonfiguruj aplikacje Python

W Namecheap w `cPanel -> Setup Python App` utworz aplikacje i ustaw:

- `Python version`: `3.11` lub nowszy dostepny w hostingu
- `Application root`: katalog repozytorium, np. `/home/<user>/import-benzara`
- `Application URL`: docelowy URL aplikacji
- `Application startup file`: `passenger_wsgi.py`
- `Application Entry point`: `application`

Projekt zawiera gotowy plik:

- `passenger_wsgi.py`

oraz alternatywnie:

- `wsgi.py`

W praktyce najbezpieczniejsza konfiguracja dla Shared Hosting to `WSGI`, nie `ASGI`.

### 3. Zainstaluj zaleznosci

Masz dwa poprawne warianty:

1. Przez SSH lub terminal w cPanel:

```bash
pip install -e .
```

2. Przez interfejs Namecheap:

- dodaj plik `requirements.txt` w katalogu aplikacji,
- w `Configuration files` wybierz `requirements.txt`,
- uruchom `Run Pip Install`.

### 4. Ustaw zmienne srodowiskowe

Minimalny zestaw:

```bash
IMPORT_BENZARA_DATA_DIR=/home/<user>/import-benzara/data
IMPORT_BENZARA_MIN_STOCK_THRESHOLD=10
IMPORT_BENZARA_SECRET_KEY=zmien-to-na-losowy-sekret
```

Opcjonalne zabezpieczenie panelu:

```bash
IMPORT_BENZARA_ADMIN_USER=admin
IMPORT_BENZARA_ADMIN_PASSWORD=strong-password
```

Po zmianie zmiennych srodowiskowych zrestartuj aplikacje w panelu Namecheap.

## Publiczny URL feedu

Po wdrozeniu publiczny URL powinien wskazywac na:

- `https://twoja-domena/feed.xml`

To ten adres nalezy wpisac do pluginu WooCommerce.

## Cron

Do automatycznej regeneracji feedu uzyj:

```bash
/home/<user>/virtualenv/import-benzara/<python-version>/bin/python /home/<user>/import-benzara/generate_latest_stock_feed.py --data-root "/home/<user>/import-benzara/data" --minimum-stock-threshold 10
```

Jesli w danym koncie Namecheap sciezka do virtualenv jest inna, uzyj tej pokazanej na stronie aplikacji w `Setup Python App`.

Cron powinien odswiezac feed tylko po poprawnym uploadzie plikow zrodlowych.

## Rekomendacje operacyjne

- panel admin zabezpiecz Basic Auth albo ochrona katalogu w panelu hostingu
- publiczny `feed.xml` pozostaw bez autoryzacji, bo plugin WooCommerce zazwyczaj pobiera plik po zwyklym HTTP(S)
- trzymaj jeden stabilny URL feedu
- nie usuwaj rekordow z niskim stockiem z feedu, tylko eksportuj je jako `outofstock`
- jesli aplikacja zwraca `500`, mozna tymczasowo wlaczyc `PassengerFriendlyErrorPages on` w `.htaccess`, zgodnie z dokumentacja Namecheap dla debugowania WSGI

## Test po wdrozeniu

Po wdrozeniu sprawdz:

1. Czy panel otwiera sie poprawnie.
2. Czy mozna wgrac `XLSX` i `CSV`.
3. Czy po kliknieciu generowania powstaje `feed.xml`.
4. Czy `feed.xml` jest publicznie dostepny.
5. Czy plugin WooCommerce poprawnie mapuje:

- `sku`
- `stock/qty`
- `stock/status`
- `stock/manage`

Synchronizuj tylko pola magazynowe.

## Zrodlo

Oficjalna instrukcja Namecheap:

- [How to work with Python App - Namecheap](https://www.namecheap.com/support/knowledgebase/article.aspx/10048/2182/how-to-work-with-python-app/)
