import pandas as pd
from functions import *
from rendering import *

# Zaladuj dzialki i kw

dane_wnioskodawcy = {
    "pesel": "----------",
    "regon": "017511575",
    "krs": "-" * 10,
    "nazwa": "SKARB PAŃSTWA - GENERALNY DYREKTOR DRÓG KRAJOWYCH I AUTOSTRAD",
    "nazwisko2": "-" * 10,
    "imie": "-" * 10,
    "imie2": "-" * 10,
    "imie_ojca": "-" * 10,
    "imie_matki": "-" * 10,
    "kraj": "POLSKA",
    "miejscowosc": "WARSZAWA",
    "ulica": "Wronia",
    "nr_budynku": "53",
    "nr_lokalu": "---",
    "kod_pocztowy": "00-874",
}


def pasek_postepu(licznik, suma):
    procent = int(round(licznik / suma * 100))
    pasek = "[" + "|" * procent + "-" * (100 - procent) + "]"
    pasek = (
        pasek[:47] + f"{procent}%" + pasek[50:]
    )  # Wstawienie procentu w odpowiednie miejsce
    print("\n" * 20)
    print(pasek)


if __name__ == "__main__":

    df_dzialki = load_dzialki(r"import/Dzialki.xlsx")
    print("Zaladowano informacje o działkach")
    df_relacje = load_relacje(r"import/Relacje.xlsx")
    print("Zaladowano informacje o właścicielach")
    df_osoby = load_osoby(r"import/Wlasciciele.xlsx")
    print("Załadowano informacje o osobach")
    df_sady = load_sady(r"import/Sady.xlsx")
    print("Załadowano informacje o sądach")
    df_GDDKIA = load_gddkia(r"import/KW-GDDKIA.xlsx")
    print("Załadowano informacje o Księgach GDDKIA i obrębach")
    dzialki_inwestycja = dzialki_w_inwestycji(df_dzialki)
    print(df_osoby)

    lista_kw = sorted(
        df_dzialki[df_dzialki["czy_inwestycja"] == True][["KW", "obreb"]]
        .dropna()
        .drop_duplicates()
        .to_dict(orient="records"),
        key=lambda x: x["KW"],
    )

    print("LISTA ZNALEZIONYCH KW DO WNIOSKÓW")
    for line in lista_kw:
        print(line["KW"], line["obreb"])
    wnioski = []
    ile_wnisokow = len(lista_kw)
    for num, kw in enumerate(lista_kw, start=1):
        # pasek_postepu(num,ile_wnisokow)
        print()
        print(f"[{num}/{ile_wnisokow}]", end=" ")
        wniosek = Wniosek(
            kw["KW"],
            kw["obreb"],
            df_dzialki,
            df_relacje,
            df_osoby,
            df_sady,
            dane_wnioskodawcy,
            df_GDDKIA,
            dzialki_inwestycja,
        )
        wniosek.print_forms()
        wnioski.append(wniosek)
    print("Zakończono tworzenie wniosków")
    for wniosek in wnioski:
        wniosek.show_stats()
