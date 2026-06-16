# Ryzyka i Zalozenia

## Zalozenia bazowe

- plugin WooCommerce bedzie importowal plik po URL,
- feed bedzie dostepny bez recznej autoryzacji,
- podstawowym formatem eksportu bedzie XML,
- operator bedzie mial mozliwosc jednorazowej konfiguracji mapowania w pluginie.

## Ryzyka wynikajace z pluginu

### 1. Import dziala po URL, nie po lokalnym pliku

To oznacza wymaganie stalej publikacji feedu i dostepnosci sieciowej.

### 2. CSV jest mniej przewidywalne

CSV przechodzi przez konwersje do XML, co dodaje:

- problemy z separatorami,
- problemy z kodowaniem,
- problemy z naglowkami.

### 3. Niektore opcje embedded variations sa podejrzane

W analizowanej wersji pluginu warto ostroznie traktowac:

- `variation_sale_price`
- `variation_backorders`
- `variation_tax_status`
- `variation_first_as_default`

Powod:

- w kodzie czesc odwolan wyglada na niespojna albo niepelnie podlaczona.

### 4. Slady wariacji po EAN sa niepelne

W kodzie sa stale dotyczace `variation_type_ean`, ale nie wyglada to na pelna, bezpieczna funkcje do oparcia projektu.

### 5. Synchronizacja po nazwie jest ryzykowna

Zmiana tytulu moze spowodowac:

- tworzenie duplikatow,
- utrate spojnosc i aktualizacji.

## Ryzyka projektowe po stronie aplikacji

### 1. Za duzo logiki po stronie pluginu

Jesli aplikacja zostawi zbyt wiele decyzji pluginowi, trudniej bedzie:

- debugowac bledy,
- testowac feed,
- utrzymywac integracje.

### 2. Brak modelu kanonicznego

Jesli kazdy dostawca bedzie mial osobny, nieformalny mapping, projekt szybko stanie sie trudny do utrzymania.

### 3. Niestabilny URL feedu

Kazda zmiana URL moze wymuszac reczna rekonfiguracje importu.

## Dzialania ograniczajace ryzyko

- generowac XML zamiast CSV,
- synchronizowac po `custom_product_id` lub `SKU`,
- wykonywac walidacje przed publikacja,
- w MVP ograniczyc zaleznosc od problematycznych opcji embedded variations,
- utrzymywac jedna stabilna strukture feedu,
- trzymac pelna historie publikacji i bledow.
