# Notatki o pluginie WP Desk

Źródła:

- [Produkt](https://wpdesk.net/products/dropshipping-xml-woocommerce/)
- [Dokumentacja](https://wpdesk.net/docs/dropshipping-xml-woocommerce/)

## Co potwierdza dokumentacja

- plugin obsługuje pliki `CSV` i `XML`,
- pozwala mapować pola produktu metodą drag and drop,
- pozwala kojarzyć aktualizacje po `SKU`, nazwie produktu, `EAN` lub własnym ID,
- posiada tryb aktualizacji istniejących produktów bez tworzenia nowych,
- pozwala wskazać, które pola WooCommerce mają być aktualizowane podczas synchronizacji,
- posiada harmonogram synchronizacji i logi importu.

## Co to oznacza dla projektu

Docelowy generator nie musi odtwarzać całego procesu importu WooCommerce. Wystarczy, że przygotuje przewidywalny plik źródłowy dla już skonfigurowanego importu WP Desk.

Najbezpieczniejszy wariant pierwszej wersji:

1. wygenerować jednolity plik CSV,
2. utrzymać spójną strukturę nagłówków,
3. zaktualizować tylko pola wymagane do synchronizacji stanów,
4. wykorzystać w pluginie tryb `update existing products only`,
5. mapować identyfikację po `SKU`.

## Wnioski wdrożeniowe

- generator powinien pracować deterministycznie i zapisywać raport walidacyjny,
- wynik powinien być prosty do ręcznego podglądu przed importem,
- trzeba przygotować zestaw testowy z małej próbki SKU,
- należy rozdzielić logikę transformacji danych od logiki przyszłego modułu zdjęć.
