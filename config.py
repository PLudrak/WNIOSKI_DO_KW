# wykreslenie pustego pola
WYKR = "-" * 10

#### Informacje podstawowe o pracy:
ROBOTA = "C-L"

DECYZJA = "DECYZJA WOJEWODY MAZOWIECKIEGO NR 176/SPEC/2024 Z DNIA 6.06.2024R. ZNAK: WIR-I.7820.1.5.2024.AW"
PELNOMOCNICTWO = "PEŁNOMOCNICTWO z dnia xxx oznaczenie: xxxx - znajduje się w aktach KW  RA1L/00004537/0"
PELNOMOCNIK = "JAN KOWALSKI"
WOJEWODZTWO = "PODLASKIE"

# dane GDDKiA
dane_gddkia = {
    "pesel": "----------",
    "regon": "017511575",
    "krs": WYKR,
    "nazwa": "SKARB PAŃSTWA - GENERALNY DYREKTOR DRÓG KRAJOWYCH I AUTOSTRAD",
    "nazwisko2": WYKR,
    "imie": WYKR,
    "imie2": WYKR,
    "imie_ojca": WYKR,
    "imie_matki": WYKR,
    "kraj": "POLSKA",
    "miejscowosc": "WARSZAWA",
    "ulica": "Wronia",
    "nr_budynku": "53",
    "nr_lokalu": "---",
    "kod_pocztowy": "00-874",
}

# dane do doręczeń - zależne od tego którego oddziału dotyczy inwestycja
dane_oddzial_gddkia = {
    "d_nazwa": "GENERALNA DYREKCJA DRÓG KRAJOWYCH I AUTOSTRAD - Oddział w Warszawie",
    "d_miejscowosc": "WARSZAWA",
    "d_ulica": "MIŃSKA",
    "d_numer_budynku": "25",
    "d_numer_lokalu": "---",
    "d_kod": "03-808",
    "d_poczta": "WARSZAWA",
}

DANE_WNIOSKODAWCY = dane_gddkia | dane_oddzial_gddkia

# co wpisać w miejsce KW jeżeli działkę dołączamy do nowej księgi która nie ma jeszcze numeru ani dzkw
NIEZALOZONA_KW_DOCELOWA = "PIERWSZA KW ZAŁOŻONA W OBREBIE W RAMACH INWESTYCJI"

# czy do pierwszego wniosku w danym obrębie dołączane są zbiorcze wypisy
# True - wszystkie wypisy z obrębu dołączone do pierwszego winosku
# False - do każdego
ZBIORCZE_WYPISY = True

# do którego wniosku
DECYZJA_W_AKTACH = "RA1L/00004537/0"

# Rodzaj rządania do wniosku
ODLACZENIE = True
PODZIAL = True
