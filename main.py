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


def load_data(path="import"):

    df_dzialki = load_dzialki(os.path.join(path, "Dzialki.xlsx"))
    print("Zaladowano informacje o działkach")

    df_relacje = load_relacje(os.path.join(path, "Relacje.xlsx"))
    print("Zaladowano informacje o właścicielach")

    df_osoby = load_osoby(os.path.join(path, "Wlasciciele.xlsx"))
    print("Załadowano informacje o osobach")

    df_sady = load_sady(os.path.join(path, "Sady.xlsx"))
    print("Załadowano informacje o sądach")

    df_GDDKIA = load_gddkia(os.path.join(path, "KW-GDDKIA.xlsx"))
    print("Załadowano informacje o Księgach GDDKIA i obrębach")

    dzialki_inwestycja = dzialki_w_inwestycji(df_dzialki)

    return df_dzialki, df_relacje, df_osoby, df_sady, df_GDDKIA, dzialki_inwestycja


def get_lista_kw(df_dzialki):
    lista = sorted(
        df_dzialki[df_dzialki["czy_inwestycja"] == True][["KW", "obreb"]]
        .dropna()
        .drop_duplicates()
        .to_dict(orient="records"),
        key=lambda x: x["KW"],
    )

    print("LISTA ZNALEZIONYCH KW DO WNIOSKÓW")
    for line in lista:
        print(line["KW"], line["obreb"])

    return lista, len(lista)


def save_stats(lista_wnioskow, filepath="export"):
    path = os.path.join(filepath, "Stats.xlsx")
    all_stats = []

    data_to_export = [wniosek.stats_to_export() for wniosek in lista_wnioskow]
    df = pd.DataFrame(data_to_export)

    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Wnioski")
    print('Zapisano raport w folderze "EXPORT')


if __name__ == "__main__":

    df_dzialki, df_relacje, df_osoby, df_sady, df_GDDKIA, dzialki_inwestycja = (
        load_data(path="import")
    )

    lista_kw, ile_wnisokow = get_lista_kw(df_dzialki)

    wnioski = []

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

    save_stats(wnioski)

    # for wniosek in wnioski:
    # wniosek.show_stats()
