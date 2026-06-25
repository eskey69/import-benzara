# Architektura projektu

## Przeglad

Projekt bedzie mial forme prostego potoku ETL:

1. `loaders` - odczyt plikow XML i XLSX
2. `normalizers` - ujednolicenie nazw pol i formatow danych
3. `matchers` - laczenie rekordow po SKU
4. `rules` - logika biznesowa cen, stanow i filtrow wysylkowych
5. `exporters` - zapis pliku wynikowego oraz raportu

## Modulowy podzial odpowiedzialnosci

### `loaders`

Odpowiada za:

- odczyt XML WooCommerce
- odczyt XLSX Benzara
- odczyt XML stanow magazynowych
- walidacje podstawowej struktury danych

### `normalizers`

Odpowiada za:

- wykrycie pola `sku` lub `_sku`
- czyszczenie SKU
- normalizacje cen
- normalizacje wag i wymiarow
- mapowanie pol do wspolnego modelu produktu

### `matchers`

Odpowiada za:

- laczenie rekordow z trzech zrodel po `normalized_sku`
- oznaczanie produktow istniejacych i nowych
- wykrywanie brakow danych

### `rules`

Odpowiada za:

- wyliczenie ceny sprzedazy
- przypisanie stanu magazynowego
- sprawdzenie oplacalnosci wysylki
- decyzje, czy produkt ma byc dodany, zaktualizowany czy pominiety

### `exporters`

Odpowiada za:

- przygotowanie pliku `d`
- przygotowanie raportu odrzuconych lub niekompletnych rekordow

## Model danych roboczych

Docelowo kazdy produkt po normalizacji powinien miec minimum:

- `normalized_sku`
- `source_woo_exists`
- `supplier_name`
- `supplier_cost`
- `stock_quantity`
- `weight`
- `length`
- `width`
- `height`
- `shipping_eligible`
- `price_target`
- `action`
- `action_reason`

## Wyniki przetwarzania

Program powinien generowac dwa typy wynikow:

- plik importowy do WooCommerce
- raport kontrolny dla operatora
