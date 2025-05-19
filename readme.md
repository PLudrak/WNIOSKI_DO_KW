# WPISY_DO_KW

## Cel projektu

Program służy do automatycznego generowania wniosków o wpis lub założenie księgi wieczystej (KW) wraz z załącznikami. Został stworzony z myślą o porządkowaniu KW działek należących do GDDKiA po podziale nieruchomości pod inwestycję drogową.

---

## Działanie skryptu (stan na 25.08.2024)

1. **Ładowanie danych o wnioskodawcy**  
   Hardcodowane w `main.py`.

2. **Ładowanie danych wejściowych z plików `.xlsx` z katalogu `import/`:**  
   - Działki  
   - Relacje działka – właściciel  
   - Dane adresowe i osobowe właścicieli  
   - Słownik kodów sądów rejonowych  
   - Dane o KW, do których dopisywane będą nieruchomości (po jednej na obręb)

3. **Tworzenie listy KW i obrębów**, dla których generowane będą wnioski

4. **Generowanie wniosków:**
   - Przypisanie KW
   - Rodzaj wniosku
   - Dane wnioskodawcy
   - Numery działek z KW w danym obrębie
   - Ustalanie adresów ewidencyjnych działek (błąd w przypadku różnych obrębów)
   - Identyfikatory właścicieli na podstawie relacji
   - Liczba właścicieli
   - Dane właścicieli
   - Dane sądu i wydziału
   - **Załączniki:**
     - Dodawane tylko do pierwszego wniosku w obrębie (pozostałe dostają odniesienie)
     - KW-PP – na stałe w kodzie
     - KW-WU – jeżeli liczba właścicieli > 2
     - Decyzja wojewody – na stałe w kodzie

5. **Generowanie plików PDF** dla wniosków

---

## Struktura katalogów

📁 WPISY_DO_KW/
├── main.py # Główny plik aplikacji
├── functions.py # Główna logika
├── requirements.txt # Zależności Pythona
├── README.md # Opis projektu
│
├── 📁 import/ # Pliki wejściowe (.xlsx)
│ ├── Wlasciciele.xlsx
│ ├── Dzialki.xlsx
│ ├── Relacje.xlsx
│ ├── Sady.xlsx
│ ├── KW-GDDKIA.xlsx
│
├── 📁 forms/ # Szablony jinja2 HTML do generowania PDF
│
└── 📁 export/ # Wygenerowane pliki PDF
└──📁 <sad rejonowy>/
└──📁 <nazwa obrębu>/
└──📁 <nr_kw>/
└── WNIOSKI.PDF

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
