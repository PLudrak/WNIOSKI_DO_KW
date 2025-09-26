# WPISY_DO_KW

## Cel projektu

Program służy do automatycznego generowania wniosków o wpis lub założenie księgi wieczystej (KW) wraz z załącznikami. Został stworzony z myślą o porządkowaniu KW działek należących do GDDKiA po podziale nieruchomości pod inwestycję drogową.

---

## Działanie skryptu (stan na 25.08.2024)

## Działanie skryptu(25.08.2024):

1.Ładowanie danych o wnioskodawcy, hardcodowanych w main.py  
2.Ładowanie danych z import/.xlsx  
  2.1 Ładowanie info o działkach  
  2.2 Ładowanie info o relacjach działka - właściciel  
  2.3 Ładowanie danych adresowych/osobowych właścicieli  
  2.4 Ładowanie tabeli słownikowej z kodami sądów rejonowych  
  2.5 Ładowanie danych z informacjami o księgach wieczystych do których będziemy dopisywać  
    nieruchomości (po jednej do każdego obrębu)  
3.Stworzenie listy numerów KW i obrębów dla których generowane będą wnioski  
4.Generowanie wniosku na podstawie załadowanych danych i listy z pkt3.:  
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


---


## TODO / Do poprawy

- [x] Formularz dla KW-ZAL
- [x] Obsługa podmiotów niebędących osobami fizycznymi
- [x] Usunięcie uczestnika2, jeżeli jest tylko jeden właściciel
- [x] KW-ZAL jako pierwszy wniosek, gdy GDDKiA nie ma działki w obrębie (preferowana opcja: przez odłączenie)
- [x] KW-WU, jeżeli właścicieli jest więcej niż dwóch
- [x] Jeżeli więcej niż 1 działka we wniosku ZAL → dodanie ich do wniosków OZN
- [x] Zbiorczy PDF do druku z kontrolą parzystości stron
- [x] Raportowanie do Excela
- [ ] Załączniki są definiowane wewnątrz funkcji – **zautomatyzować**
- [ ] Połączyć `dzialki_odlaczane` i `dzialki_oznaczone` w jedną zmienną
- [ ] Funkcja `obreb` w klasie `Wniosek` → zamienić na „dane ewidencyjne”
- [ ] Automatyczne przenoszenie załączników do folderów
- [ ] Refaktoryzacja `main.py` i `functions.py`, klasa `Wniosek` do osobnego pliku
- [ ] Logowanie do pliku `.txt`

---

## Wymagania

Zainstaluj wymagane pakiety:
```bash
pip install -r requirements.txt
