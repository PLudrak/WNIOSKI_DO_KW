Wnioski o wpis lub założenie kw oraz załączniki
Program jest przygotowany do jednego konkretnego celu:
Porządkowania kw działek należących do GDDKIA po podziale nieruchomości pod inwestycję drogową.


Działanie skryptu(25.08.2024):
1.Ładowanie danych o wnioskodawcy, hardcodowanych w main.py
2.Ładowanie danych z import/.xlsx
	2.1 Ładowanie info o działkach
	2.2 Ładowanie info o relacjach działka - właściciel
	2.3 Ładowanie danych adresowych/osobowych właścicieli
	2.4 Ładowanie tabeli słownikowej z kodami sądów rejonowych
	2.5 Ładowanie danych z informacjami o księgach wieczystych do których będziemy dopisywać
		nieruchomości (po jednej do każdego obrębu)
3.Stworzenie listy numerów KW i obrębów dla których generowane będą wnioski
4.Generowanie wniosku na podstawie załadowanych danych i listy z pkt3. :
	4.1 Przypisanie KW do wniosku
	4.2 Przypisanie rodzaju wniosku
	4.3 Przepisanie danych wnioskodawcy do wniosku
	4.4 Przypisanie numerów działek z KW w danym obrebie (pkt3) do wniosku
	4.5 Ustalenie adresu ewid. dla dzialek z wniosku (Obreb, Nr obrebu, Gmina, Powiat),
		dzialki w roznych obrebach spowoduja bład
	4.6 Znalezienie identyfikatorow wlascicieli na podstawie tabeli z relacjiami
	4.7 Okreslenie liczby wlascicieli
	4.8 Pobieranie danych o wlascicielach do wniosku
	4.9 Pobieranie danych o sądzie i wydziale odpowiednim dla danego wniosku
	4.10 Dodanie zalacznikow 
		4.10.1 Okreslenie czy wniosek jest pierwszym skladanym w danym obrebie, 
			zalaczniki sa dodawane do pierwszego wniosku w danym obrebie, 
			dla pozostalych dodawany jest odnosnik do pierwszego wniosku 
			(Pierwszenstwo okresla sie na podstawie alfabetycznej listy numerów kw)
		4.10.2 KW-PP na stałe w kodzie
		4.10.3 KW-WU wstepuje jezeli liczba wlascicieli > 2 (nie miesci sie w glownym wniosku)
		4.10.4 Decyzja wojewody na stałe w kodzie
5.Generowanie plików pdf dla wniosków. 

Struktura projektu:
📁 WPISY_DO KW/
├── main.py                 # Główny plik startowy aplikacji
├── functions.py            # Główna logika programu
├── requirements.txt        # Lista zależności Pythona
├── README.md               # Opis projektu
│
├── 📁 import/              # Pliki wejściowe, .xslx utworzone na podstawie SWDE/GML
│   ├── Wlasicicele.xlsx
│   ├── Dzialki.xlsx
│   ├──	Relacje.xlsx
│   ├──	Sady.xlsx
│   ├──	KW-GDDKIA.xlsx
│   └── Relacje.xlsx
│
├── 📁 forms/             # Templatki jinja2.html do generowania wnioskow w pdf
│
└── 📁 export/            #kolejne foldery tworzą się automatycznie
    └──📁 <sad rejonowy>/
        └──📁 <nazwa obrebu>/
	        └──📁 <nr_kw>/
			    └──WNIOSKI.PDF
				
Do poprawy/zrobienia:
[x] stworzyc formulaz dla KW-ZAL
[x] poprawić wpisywanie danych dla podmiotów nie będących osobami fizycznymi
[x] wykreślic uczestnika2 jezeli jeden walsciciel
[x] Jeżeli gddkia nie ma dzialki w obrebie, pierwszy wniosek powinien byc KW-ZAL a nie KW-WPIS,
		zastanowic sie czy to powinno byc zalozenie przez odlaczenie czy zalozenie nowej kw
		dla nieruchomosci ktora wczesniej kw nie miala, bardziej sklaniam sie do opcji przez odlaczenie, 
		bo bedzie miala taka sama podstawe jak wpisy
[x] jeżeli wiecej niż dwie osoby w KW-ZAL dodaj KW-WU
[x] jezeli wiecej niz 1 dzialka we wniosku zal to dodaj je do wnioskow ozn
[x] tworzenie zbiorczego pdfa do druku, z kontrolą parzystości stron 
[x] raportowanie do excela
[ ] Załączniki są definiowane wewnątrz funkcji - trzeba to bardziej zautomatyzowac
[ ] uporządkować dzialki w inwestycji i okolice
	dzialki_odlaczane i dzialki_oznaczone można połączyć w jedną zmienną 
[ ] Poprawic funkcje obreb w klasie Wniosek -> zmienic na dane ewidencyjne czy cos 
[ ] Automatyczne przenoszenie załączników do folderów. 
[ ] uporządkować main.py i functions.py - ewentualnie klase wniosek do oddzielnego pliku
[ ] logowanie do txt
