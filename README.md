# import-benzara

Serwerowa aplikacja do generowania publicznego feedu `XML` dla pluginu `Dropshipping XML WooCommerce PRO` na podstawie danych Benzara.

## Co robi aplikacja

Aplikacja:

- przyjmuje plik bazowy `XLSX` z pelnym katalogiem Benzara,
- przyjmuje plik `Inventory CSV` ze stanami magazynowymi,
- laczy dane po `SKU`,
- stosuje prog stocku `10` sztuk,
- wszystko ponizej progu eksportuje jako `stock_qty = 0`,
- ustawia `stock_status` na `instock` albo `outofstock`,
- publikuje publiczny `feed.xml` gotowy do podpiecia w WooCommerce.

## Logika biznesowa

Docelowa regula:

- `Qty >= 10` -> eksportuj realny stock
- `Qty < 10` -> eksportuj `0`
- brak SKU w inventory -> eksportuj `0`

Produkty ze stanem `0` nie powinny byc pomijane w feedzie. Powinny byc eksportowane jako `outofstock`, a ich ukrywanie ma byc realizowane przez ustawienia WooCommerce.

## Dlaczego ta wersja nadaje sie na Namecheap

Projekt zostal przygotowany pod model:

- aplikacja Python uruchomiona jako `WSGI app`,
- panel WWW do uploadu plikow i generowania feedu,
- publiczny endpoint `feed.xml`,
- opcjonalny cron do odswiezania feedu z najnowszych uploadow.

Repo zawiera:

- `passenger_wsgi.py`
- `wsgi.py`
- `generate_latest_stock_feed.py`
- `requirements.txt`
- panel Flask
- CLI do generowania feedu
- dokumentacje wdrozenia

## Struktura projektu

- `src/import_benzara/` - kod aplikacji
- `src/import_benzara/webapp.py` - panel WWW
- `src/import_benzara/stock_pipeline.py` - generator XML stock feedu
- `data/uploads/` - wgrane pliki zrodlowe
- `data/generated/latest/` - aktualny feed i raporty
- `data/generated/runs/` - historia przebiegow
- `docs/NAMECHEAP-DEPLOYMENT.md` - instrukcja wdrozenia

## Instalacja zaleznosci

Lokalnie:

```bash
pip install -e .
```

Na Namecheap mozna tez uzyc pliku `requirements.txt` w `cPanel -> Setup Python App -> Configuration files -> Run Pip Install`.

## Najwazniejsze komendy

### 1. Legacy CSV generator

Historyczny tryb CSV nadal jest dostepny:

```bash
python -m import_benzara generate --inventory path/to/inventory.csv --catalog path/to/catalog.xlsx --output path/to/output.csv
```

### 2. Stock feed XML

```bash
python -m import_benzara generate-stock-feed ^
  --inventory "C:\path\to\inventory.csv" ^
  --catalog "C:\path\to\catalog.xlsx" ^
  --output-xml "C:\path\to\feed.xml" ^
  --minimum-stock-threshold 10
```

### 3. Stock feed z najnowszych uploadow

```bash
python -m import_benzara generate-latest-stock-feed --data-root "C:\path\to\data" --minimum-stock-threshold 10
```

Na Namecheap bez `pip install -e .` bezpieczniejszy jest wrapper:

```bash
python generate_latest_stock_feed.py --data-root "C:\path\to\data" --minimum-stock-threshold 10
```

### 4. Lokalny panel WWW

```bash
python -m import_benzara serve --data-root "C:\path\to\data" --host 127.0.0.1 --port 8000
```

Po uruchomieniu:

- panel admin: `http://127.0.0.1:8000/`
- publiczny feed: `http://127.0.0.1:8000/feed.xml`

## Zmienne srodowiskowe

- `IMPORT_BENZARA_DATA_DIR` - katalog danych aplikacji
- `IMPORT_BENZARA_MIN_STOCK_THRESHOLD` - domyslny prog stocku
- `IMPORT_BENZARA_SECRET_KEY` - sekret Flask
- `IMPORT_BENZARA_ADMIN_USER` - opcjonalny login Basic Auth
- `IMPORT_BENZARA_ADMIN_PASSWORD` - opcjonalne haslo Basic Auth

## Co publikuje aplikacja

Po kazdym poprawnym przebiegu:

- `data/generated/latest/feed.xml`
- `data/generated/latest/feed.summary.json`
- `data/generated/latest/feed.inventory-only.csv`
- `data/generated/latest/feed.catalog-only.csv`

## Konfiguracja WooCommerce

W pluginie `Dropshipping XML WooCommerce PRO` ustaw:

- URL pliku: publiczny `feed.xml`
- identyfikacja produktu: `SKU`
- wezel produktu: `catalog/products/product`
- mapowanie pol: `sku`, `stock/qty`, `stock/status`, `stock/manage`

Synchronizuj tylko pola magazynowe.

## Wdrozenie

Instrukcja wdrozenia znajduje sie tutaj:

- [docs/NAMECHEAP-DEPLOYMENT.md](./docs/NAMECHEAP-DEPLOYMENT.md)
