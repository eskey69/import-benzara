# Dokumentacja do budowy aplikacji przygotowującej pliki importu dla `Dropshipping XML WooCommerce PRO`

## 1. Zakres i źródło analizy

Analiza została wykonana na podstawie lokalnej paczki:

- `C:/Users/skrupa/Documents/!_horpach.com/woocommerce-dropshipping-xml.zip`

Wersja dodatku z paczki:

- `Dropshipping XML WooCommerce PRO 2.12.1`

Najważniejsze pliki źródłowe użyte do odtworzenia działania:

- `woocommerce-dropshipping-xml/woocommerce-dropshipping-xml.php`
- `woocommerce-dropshipping-xml/src/Plugin/Plugin.php`
- `woocommerce-dropshipping-xml/vendor_prefixed/wpdesk/woocommerce-dropshipping-xml-core/src/Form/Fields/ImportFileFormFields.php`
- `woocommerce-dropshipping-xml/vendor_prefixed/wpdesk/woocommerce-dropshipping-xml-core/src/Form/Fields/ImportXmlSelectorFormFields.php`
- `woocommerce-dropshipping-xml/vendor_prefixed/wpdesk/woocommerce-dropshipping-xml-core/src/Form/Fields/ImportCsvSelectorFormFields.php`
- `woocommerce-dropshipping-xml/vendor_prefixed/wpdesk/woocommerce-dropshipping-xml-core/src/Form/Fields/ImportMapperFormFields.php`
- `woocommerce-dropshipping-xml/vendor_prefixed/wpdesk/woocommerce-dropshipping-xml-core/src/Form/Fields/ImportOptionsFormFields.php`
- `woocommerce-dropshipping-xml/vendor_prefixed/wpdesk/woocommerce-dropshipping-xml-core/src/Action/Process/ImportProcessAction.php`
- `woocommerce-dropshipping-xml/vendor_prefixed/wpdesk/woocommerce-dropshipping-xml-core/src/Service/Creator/ProductCreatorService.php`
- `woocommerce-dropshipping-xml/vendor_prefixed/wpdesk/woocommerce-dropshipping-xml-core/src/Service/Mapper/Product/*.php`

## 2. Cel dokumentu

Ten dokument ma dać kompletną podstawę do zbudowania aplikacji, która:

1. pobiera dane od dostawców,
2. normalizuje je do jednego wewnętrznego modelu,
3. generuje plik XML albo CSV,
4. publikuje plik pod adresem URL,
5. pozwala skonfigurować import w badanym dodatku WooCommerce bez ręcznego zgadywania struktury.

## 3. Jak rzeczywiście działa plugin

Importer ma cztery logiczne kroki:

1. Krok 1: pobranie pliku z URL.
2. Krok 2: wybór rekordu produktu.
3. Krok 3: mapowanie pól produktu.
4. Krok 4: opcje synchronizacji i uruchomienie importu.

### 3.1. Wejście do pluginu

Plugin nie importuje pliku lokalnego z dysku użytkownika. W badanym kodzie wejście to URL pobierany przez cURL.

W praktyce oznacza to, że nowa aplikacja musi kończyć pracę publikacją feedu pod publicznym albo co najmniej osiągalnym adresem HTTP(S).

Domyślnie interfejs pluginu przewiduje tylko:

- `file_url`
- ukryty klient `curl_http`

W UI nie ma pola na:

- Basic Auth,
- tokeny,
- niestandardowe nagłówki.

Kod ma filtry pozwalające to rozszerzyć programistycznie, ale nie ma tego "out of the box".

## 4. Obsługiwane formaty plików

### 4.1. XML

Obsługiwane MIME:

- `text/xml`
- `application/xml`

Walidacja XML jest rzeczywista: plik musi się parsować jako poprawny XML.

### 4.2. CSV

Obsługiwane MIME:

- `text/plain`
- `text/csv`
- `text/x-csv`
- `application/csv`
- `application/x-csv`

CSV nie jest importowane bezpośrednio. Najpierw jest konwertowane do wewnętrznego XML:

```xml
<data>
  <node>
    <column_1><![CDATA[...]]></column_1>
    <column_2><![CDATA[...]]></column_2>
  </node>
</data>
```

Jeśli nagłówki CSV są poprawne, plugin użyje ich jako nazw elementów XML zamiast `column_1`, `column_2`, itd.

### 4.3. Auto-detekcja separatora i kodowania CSV

Separator CSV jest wykrywany z próby danych. Obsługiwane kandydaty:

- `;`
- `,`
- tab
- `|`
- `:`

Kodowanie źródłowe CSV jest wykrywane automatycznie, ale domyślny fallback w konwerterze to `WINDOWS-1250`.

Wniosek dla aplikacji:

- jeśli generujemy CSV, najlepiej zapisywać je jako UTF-8,
- separator ustawić jawnie i stabilnie, najlepiej `;` albo `,`,
- nagłówki powinny być krótkie i bez znaków specjalnych.

## 5. Wewnętrzna logika przetwarzania

### 5.1. XML jest formatem docelowym całego importu

Niezależnie od tego, czy dostarczymy XML czy CSV, finalny import działa na XML oraz XPath-ach.

To jest kluczowy wniosek projektowy:

- jeśli aplikacja ma obsłużyć proste, złożone i wariantowe katalogi, rekomendowany format eksportu to XML,
- CSV warto traktować jako tryb uproszczony dla płaskich katalogów.

### 5.2. Wybór rekordu produktu

Dla XML plugin analizuje strukturę dokumentu i próbuje wskazać powtarzalny element produktu. Algorytm preferuje elementy:

- często występujące,
- położone płytko w drzewie,
- mieszczące się do głębokości 4 poziomów.

Wniosek dla aplikacji:

- produkt powinien być powtarzalnym, jednoznacznym węzłem,
- najlepszy układ to np. `/catalog/products/product`,
- nie warto umieszczać równie licznych powtarzalnych węzłów wyżej niż `product`.

## 6. Jakie typy produktów obsługuje plugin

Plugin wspiera:

- produkt prosty,
- produkt zmienny,
- produkt zewnętrzny / afiliacyjny.

Dla produktów zmiennych wspierane są dwa podejścia:

1. model wierszowy:
   - każda wariacja jest osobnym rekordem,
   - produkt główny i wariacje są wiązane po nazwie, SKU, custom ID albo wspólnym identyfikatorze grupy;
2. model zagnieżdżony XML:
   - wariacje są osadzone jako dziecko produktu,
   - plugin odczytuje je osobnym XPath-em z wnętrza rekordu produktu.

## 7. Pola mapowane przez plugin

### 7.1. Pola podstawowe produktu

Plugin potrafi mapować:

- `title`
- `content` - pełny opis
- `excerpt` - krótki opis
- `product_type`
- `virtual`
- `external_url`
- `button_text`
- `price`
- `sale_price`
- `SKU`
- `custom_id`
- `ean` - jeśli aktywna integracja EAN

### 7.2. Podatki i ceny

Obsługiwane pola:

- `tax_status`
- `tax_class`
- mapowanie zewnętrznej klasy podatkowej na klasę WooCommerce
- modyfikatory cen

Modyfikatory cen mogą działać warunkowo, więc aplikacja może:

- generować cenę końcową już po swojej stronie,
- albo wystawiać cenę bazową i pozostawić korekty pluginowi.

Rekomendacja:

- jeżeli aplikacja ma być deterministyczna i łatwa do testowania, licz cenę końcową po stronie aplikacji,
- modyfikatory pluginu traktuj jako opcję awaryjną, nie jako główny silnik wyceny.

### 7.3. Stany magazynowe

Obsługiwane pola:

- `manage_stock`
- `stock`
- `backorders`
- `low_stock_amount`
- `stock_status`
- `sold_individually`

Jeśli `manage_stock = true`, plugin realnie ustawia ilość oraz status `instock` / `outofstock`.

### 7.4. Wysyłka i gabaryty

Obsługiwane pola:

- `weight`
- `product_length`
- `product_width`
- `product_height`
- `product_shipping_class`

### 7.5. Kategorie

Plugin obsługuje trzy tryby:

1. jedna stała kategoria dla wszystkich produktów,
2. mapowanie zewnętrznych kategorii na istniejące kategorie WooCommerce,
3. budowanie drzewa kategorii na podstawie stringa z separatorem.

Dodatkowe zachowania:

- można importować tylko produkty z mapowanych kategorii,
- można automatycznie tworzyć brakujące kategorie,
- można dodawać produkt tylko do liścia albo do wszystkich poziomów drzewa.

### 7.6. Atrybuty

Plugin wspiera dwa modele atrybutów:

1. tablica par `nazwa -> wartość`,
2. pojedynczy string, np. `Kolor:Czarny,Rozmiar:XL`.

Można zapisywać atrybuty:

- jako zwykły tekst produktu,
- albo jako taksonomie WooCommerce.

### 7.7. Tagi

Tagi są rozdzielane separatorem, domyślnie przecinkiem. Brakujące tagi są tworzone automatycznie.

### 7.8. Obrazy

Plugin obsługuje:

- listę URL-i obrazów,
- wiele URL-i rozdzielonych separatorem,
- skanowanie `img src="..."` jeśli w polu są całe tagi HTML.

Dodatkowe opcje:

- nie dodawaj obrazu głównego do galerii,
- nie nadpisuj galerii, tylko dopisuj obrazy.

### 7.9. Meta i integracje dodatkowe

Plugin obsługuje także:

- własne meta WooCommerce,
- Yoast SEO,
- GPSR for WooCommerce,
- ACF dla pól prostych i części pól z grup.

## 8. Identyfikacja produktu przy synchronizacji

W kroku opcji importu można wskazać, po czym plugin rozpoznaje produkt:

- `sku`
- `ean`
- `name`
- `custom_product_id`

To jest jedna z najważniejszych decyzji dla nowej aplikacji.

### Rekomendacja

Nie opierać synchronizacji na nazwie produktu.

Najlepsze opcje:

1. `custom_product_id` - jeśli aplikacja kontroluje stabilny identyfikator,
2. `sku` - jeśli dostawca gwarantuje jego niezmienność i unikalność,
3. `ean` - tylko jeśli rzeczywiście jest obecny i spójny.

## 9. Produkty usunięte z feedu

Plugin potrafi po imporcie obsłużyć produkty, które kiedyś były w feedzie, a teraz zniknęły.

Dostępne strategie:

- nic nie rób,
- ustaw stan magazynowy na `0`,
- przenieś do kosza.

To oznacza, że aplikacja musi mieć bardzo przewidywalny eksport:

- pełny feed do synchronizacji pełnej,
- albo osobny tryb eksportu przyrostowego, ale bez używania opcji czyszczenia po stronie pluginu.

## 10. Warunki logiczne

Plugin ma własny silnik warunków logicznych. Pozwala pominąć rekord produktu, jeśli nie spełnia reguł.

Obsługiwane typy to m.in.:

- equals
- not equals
- contains
- not contains
- empty
- not empty
- higher
- lower

Wartości porównawcze mogą mieć wiele wariantów rozdzielanych znakiem `|`.

Rekomendacja:

- krytyczne filtrowanie asortymentu lepiej zrobić w aplikacji,
- warunki pluginu traktować jako dodatkowy bezpiecznik administracyjny.

## 11. Harmonogram i batch processing

Importer działa wsadowo.

Domyślny batch:

- `30` produktów na przebieg

Można ustawić:

- dni tygodnia,
- godziny co 15 minut.

To nie wpływa na format pliku, ale wpływa na architekturę aplikacji:

- feed powinien być dostępny stale pod stałym URL,
- nie warto generować plików jednorazowych z krótkim czasem życia.

## 12. Rekomendowany format wyjściowy dla nowej aplikacji

## Rekomendacja główna: generować XML, nie CSV

Powody:

- XML jest natywnie obsługiwany przez plugin.
- XML pozwala wygodnie eksportować warianty jako zagnieżdżone elementy.
- XML jest lepszy dla opisów HTML i list obrazów.
- XML omija problemy z separatorami CSV, kodowaniem i normalizacją nagłówków.
- XML daje bardziej czytelne XPath-y w kreatorze mapowania.

### Kiedy CSV ma sens

CSV ma sens tylko wtedy, gdy:

- katalog jest płaski,
- nie potrzebujemy zagnieżdżonych wariantów,
- atrybuty, obrazy i tagi mogą być sklejane w stringi.

## 13. Rekomendowany model XML dla aplikacji

Proponowany, stabilny układ:

```xml
<catalog>
  <products>
    <product>
      <id>BENZ-001</id>
      <name><![CDATA[Krzesło biurowe]]></name>
      <sku>BENZ-001</sku>
      <ean>5901234567890</ean>
      <description><![CDATA[<p>Pełny opis produktu</p>]]></description>
      <short_description><![CDATA[Krótki opis produktu]]></short_description>
      <pricing>
        <regular>499.90</regular>
        <sale>449.90</sale>
        <tax_status>taxable</tax_status>
        <tax_class></tax_class>
      </pricing>
      <stock>
        <manage>true</manage>
        <qty>12</qty>
        <status>instock</status>
        <backorders>no</backorders>
        <low_stock>2</low_stock>
      </stock>
      <shipping>
        <weight>9.5</weight>
        <length>60</length>
        <width>60</width>
        <height>110</height>
        <class_id></class_id>
      </shipping>
      <categories>
        <category>Biuro</category>
        <category>Krzesła</category>
        <tree>Biuro &gt; Krzesła</tree>
      </categories>
      <tags>
        <tag>biuro</tag>
        <tag>ergonomia</tag>
      </tags>
      <images>
        <image>https://example.com/images/benz-001-1.jpg</image>
        <image>https://example.com/images/benz-001-2.jpg</image>
      </images>
      <attributes>
        <attribute>
          <name>Kolor</name>
          <value>Czarny</value>
        </attribute>
        <attribute>
          <name>Materiał</name>
          <value>Metal</value>
        </attribute>
      </attributes>
      <meta>
        <field>
          <key>_brand</key>
          <value>Benzara</value>
        </field>
      </meta>
      <variations>
        <variation>
          <id>BENZ-001-BLK</id>
          <sku>BENZ-001-BLK</sku>
          <price>499.90</price>
          <sale_price>449.90</sale_price>
          <stock_qty>4</stock_qty>
          <stock_status>instock</stock_status>
          <images>
            <image>https://example.com/images/benz-001-black.jpg</image>
          </images>
          <attributes>
            <attribute>
              <name>Kolor</name>
              <value>Czarny</value>
            </attribute>
            <attribute>
              <name>Rozmiar</name>
              <value>M</value>
            </attribute>
          </attributes>
        </variation>
      </variations>
    </product>
  </products>
</catalog>
```

## 14. Dlaczego taki model jest dobry dla pluginu

### 14.1. Stabilny węzeł produktu

`/catalog/products/product` jest:

- płytki,
- jednoznaczny,
- łatwy do wybrania w kroku 2.

### 14.2. Relative XPath

Po wybraniu węzła `product` większość mapowań będzie prosta:

- `name`
- `sku`
- `pricing/regular`
- `stock/qty`
- `shipping/weight`
- `images/image`
- `attributes/attribute[1]/name`
- `variations/variation`

### 14.3. Wsparcie dla wariantów zagnieżdżonych

Ten model pozwala użyć najlepszego trybu wariantów:

- `Variable products are embedded as child tags in XML`

To jest najbardziej naturalny tryb dla aplikacji, która sama generuje feed.

## 15. Minimalny kontrakt danych dla MVP aplikacji

### 15.1. Wewnętrzny model aplikacji

Aplikacja powinna mieć własny model kanoniczny niezależny od dostawcy, np.:

- `supplier_id`
- `product_id`
- `parent_product_id`
- `type`
- `name`
- `sku`
- `ean`
- `description_html`
- `short_description_html`
- `regular_price`
- `sale_price`
- `currency`
- `manage_stock`
- `stock_qty`
- `stock_status`
- `backorders`
- `weight`
- `length`
- `width`
- `height`
- `shipping_class_code`
- `categories[]`
- `category_tree[]`
- `tags[]`
- `images[]`
- `attributes[]`
- `meta[]`
- `variations[]`
- `status_flags`

### 15.2. Pola obowiązkowe w praktyce

Technicznie plugin pozwala stworzyć rekord nawet z ubogimi danymi, ale dla sensownej synchronizacji minimalny zestaw powinien zawierać:

- stabilny identyfikator synchronizacji: `custom_product_id` albo `sku`
- `name`
- `product_type`
- `price` albo przynajmniej komplet stock/status
- dla wariantów: co najmniej jeden atrybut wariacyjny

## 16. Rekomendowany zakres MVP aplikacji

### Faza 1

- import danych od dostawcy do modelu kanonicznego,
- walidacja rekordów,
- generowanie XML,
- publikacja pliku pod URL,
- eksport przykładowych XPath-ów do konfiguracji pluginu,
- podgląd produktu i wariantów przed publikacją.

### Faza 2

- profile wielu dostawców,
- mapowanie kategorii po stronie aplikacji,
- reguły cenowe,
- reguły filtrowania,
- historia publikacji feedów,
- wersjonowanie wygenerowanych plików.

### Faza 3

- generowanie też trybu CSV,
- integracja z prywatnymi źródłami i auth,
- automatyczne odświeżanie feedów,
- monitoring jakości danych.

## 17. Walidacje, które aplikacja powinna wykonywać przed publikacją

### 17.1. Walidacje ogólne

- każdy produkt ma stabilny identyfikator,
- produkt ma typ `simple`, `variable` albo `external`,
- ceny są liczbami dziesiętnymi z kropką albo dają się bezpiecznie znormalizować,
- stany magazynowe są liczbami,
- URL-e obrazów są pełnymi URL-ami HTTP(S),
- XML jest poprawny i kodowany w UTF-8,
- plik jest dostępny pod URL bez ręcznej autoryzacji w przeglądarce.

### 17.2. Walidacje wariantów

- każdy wariant ma co najmniej jeden atrybut różnicujący,
- kombinacja atrybutów wariantu jest unikalna,
- SKU wariantu nie dubluje innego produktu lub wariantu,
- jeśli produkt jest `variable`, to ma realne warianty albo aplikacja umie zdegradować go do `simple`.

### 17.3. Walidacje kategorii i tagów

- brak pustych kategorii po splitach separatorów,
- brak pustych tagów,
- separator kategorii drzewa nie występuje wewnątrz nazwy kategorii.

### 17.4. Walidacje meta

- klucze meta są zgodne z `sanitize_key`,
- aplikacja nie generuje kluczy z odstępami, polskimi znakami i dużymi literami, jeśli mają być zachowane 1:1.

## 18. Ograniczenia i pułapki wykryte w kodzie pluginu

### 18.1. Feed musi być osiągalny po URL

To nie jest opcjonalne. Badany przepływ opiera się o pobieranie pliku z URL przez cURL.

### 18.2. CSV jest formatem drugiej klasy

CSV działa, ale finalnie i tak jest zamieniane do XML. Dla złożonych katalogów będzie bardziej kłopotliwe niż własny XML.

### 18.3. Opisy HTML najlepiej podawać w CDATA

To jest najbezpieczniejsza forma dla pełnych opisów i krótkich opisów.

### 18.4. Kilka pól embedded variations wygląda na źle podłączone w kodzie

W analizowanej wersji 2.12.1 pola wariantów zagnieżdżonych wyglądają na niespójnie spięte po stronie PHP:

- `variation_sale_price`
- `variation_backorders`
- `variation_tax_status`
- `variation_first_as_default`

W kodzie serwisów embedded variations część odwołań idzie do stałych pól produktu głównego zamiast do stałych wariantu, a checkbox "first variation as default" nie jest realnie używany przez logikę ustawiania domyślnej wariacji.

Wniosek:

- nie opierać projektu aplikacji na tych opcjach bez testu end-to-end na środowisku WordPress,
- w MVP traktować te pola jako potencjalnie niestabilne.

### 18.5. Istnieją ślady nieużytej funkcjonalności wariantów po EAN

W kodzie są stałe `variation_type_ean`, ale nie są realnie podpięte do formularza i logiki importu.

Wniosek:

- nie projektować aplikacji pod warianty grupowane po EAN w tej wersji pluginu.

## 19. Rekomendowana konfiguracja pluginu dla nowej aplikacji

Jeżeli aplikacja będzie generować rekomendowany XML:

1. Krok 1: podać URL feedu XML.
2. Krok 2: wybrać węzeł produktu `product`.
3. Krok 3:
   - typ produktu: `simple` albo `variable`,
   - identyfikator produktu: `custom_id` albo `sku`,
   - opisy z mapowaniem XPath,
   - obrazy z `images/image`,
   - kategorie z `categories/category` albo `categories/tree`,
   - warianty: tryb embedded, XPath `variations/variation`.
4. Krok 4:
   - `Import into products on the basis of`: `Custom product ID` albo `SKU`,
   - zaznaczyć pola do synchronizacji,
   - ustawić zachowanie dla produktów usuniętych z feedu.

## 20. Decyzje architektoniczne dla nowej aplikacji

### Decyzja 1

Wewnętrzny model aplikacji musi być niezależny od układu jednego dostawcy.

### Decyzja 2

Domyślny eksporter powinien tworzyć XML w stabilnym, własnym schemacie.

### Decyzja 3

Aplikacja powinna publikować feed pod stałym URL, a nie generować plik "do pobrania ręcznie".

### Decyzja 4

Mapowanie do pluginu należy uprościć do gotowego profilu referencyjnego, zamiast wymagać za każdym razem ręcznego przeciągania XPath-ów.

### Decyzja 5

Obsługę problematycznych funkcji embedded variations trzeba oznaczyć jako "testowane osobno" albo przesunąć poza MVP.

## 21. Najkrótsza ścieżka do wdrożenia

Najbezpieczniejszy plan budowy aplikacji:

1. Ustalić własny kanoniczny model produktu i wariantu.
2. Zaimplementować eksport do rekomendowanego XML.
3. Dodać walidator XML i walidator biznesowy rekordów.
4. Dodać publikację feedu pod stałym URL.
5. Przygotować jeden wzorcowy profil mapowania w pluginie.
6. Dopiero potem dodawać CSV, zaawansowane reguły i integracje dodatkowe.

## 22. Podsumowanie

Najważniejszy wniosek z analizy jest prosty:

- aplikację warto projektować pod eksport XML,
- synchronizację warto opierać na `custom_product_id` albo `sku`,
- warianty najlepiej eksportować jako zagnieżdżone elementy XML,
- feed musi być dostępny po URL,
- kilka opcji embedded variations w wersji 2.12.1 wymaga ostrożności i testów integracyjnych.

W praktyce oznacza to, że nowa aplikacja nie powinna być "generatorem dowolnych plików", tylko kontrolowanym publisherem jednego, przewidywalnego formatu XML dla tego konkretnego importera.
