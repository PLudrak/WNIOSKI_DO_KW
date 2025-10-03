import pandas as pd
from wniosek import *
from rendering import *
from pdf_handling import *
from obciazenia import get_obciazenia, get_obciazenia_bez_odlaczen
from attachments import przenies_zalaczniki

# dane GDDKiA
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


def get_lista_kw(df_dzialki):
    """Pobiera wszystkie numery KW z dzialek będących w inwestycji, zwraca listę kw i liczbę znalezionych działek"""

    # filtruj wiersze gdzie "czy_inwestycja" == True, wybiera tylko pola KW i obręb, usuwa wiersze w których brakuje
    # numerów ksiąg wieczystych, usuwa duplikaty (obu wierszy razem), sortuje alfabetycznie wg klucza KW
    # (w przyszłości dobrze żeby zwracało też listę działek z inwestycji które nie mają KW, więc należy je założyć)

    df_inwestycja = df_dzialki[df_dzialki["czy_inwestycja"] == True][
        ["KW", "obreb", "jr"]
    ]
    df_kw = df_inwestycja.dropna(subset=["KW"])
    lista = sorted(
        df_kw[["KW", "obreb", "jr"]]
        .dropna()
        .drop_duplicates()
        .to_dict(orient="records"),
        key=lambda x: x["KW"],
    )

    # dzialki w inwestycji bez KW
    dzialki_bez_kw = df_inwestycja[
        df_inwestycja["KW"].isna() | (df_inwestycja["KW"] == "")
    ]

    lista_bez_kw = dzialki_bez_kw.drop_duplicates().to_dict(orient="records")

    # drukuje znalezionych numerów KW i obrębów
    print(f"LISTA ZNALEZIONYCH KW DO WNIOSKÓW [{len(lista)}]")
    for line in lista:
        print(line["KW"], line["obreb"])
    print(f"\nDZIAŁKI W INWESTYCJO DO ZALOZENIA KW [{len(lista_bez_kw)}]")
    for dz in lista_bez_kw:
        print(dz["jr"])
    return lista, len(lista), lista_bez_kw, len(lista_bez_kw)


def save_stats(lista_wnioskow: list[Wniosek], filepath="export"):
    """Połącz statystyki każdego z wniosków i zapisz je w formacie '.xslx'"""

    # ścieżka zapisu
    path = os.path.join(filepath, "Stats.xlsx")

    # łączenie danych z poszczególnych wniosków w jedną listę
    data_to_export = [wniosek.stats_to_export() for wniosek in lista_wnioskow]
    # konwersja listy na DataFrame (pandas)
    df = pd.DataFrame(data_to_export)
    # zapis do pliku
    while True:
        try:
            with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Wnioski")
                setup_excel(df, writer)
            print('Zapisano raport w folderze "EXPORT"')
            break
        except Exception as e:
            print(f"Błąd zapisu statystyk: {e}")
            print("Spróbować ponownie? (T/N)")
            odp = input().strip().lower()
            if odp != "t" and odp != "y":
                print("Zapis przerwany.")
                break


def setup_excel(df, writer):
    workbook = writer.book
    worksheet = writer.sheets["Wnioski"]
    # formatowanie nagłowka
    header_fromat = workbook.add_format(
        {"bold": True, "align": "left", "valign": "vcenter"}
    )

    # ustawienie formatu nagłówka
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_fromat)

    # zamrozenie pierwszego wiersza
    worksheet.freeze_panes(1, 0)

    # filter do naglowkow
    worksheet.autofilter(0, 0, 0, len(df.columns) - 1)

    # dopasowanie szerokosci na podstawie ngałówka
    width = [16, 6, 17, 9, 9, 9, 9, 16, 8, 10, 12, 10, 12, 12, 10, 10, 10, 10, 5, 6, 6]
    for i, width in enumerate(width):
        worksheet.set_column(i, i, width)


if __name__ == "__main__":
    print("Rozpoczeto ładowanie danych")
    (
        df_dzialki,
        df_relacje,
        df_osoby,
        df_sady,
        df_GDDKIA,
        dzialki_inwestycja,
        df_obciazenia,
        df_zalaczniki,
    ) = load_data(path="import")

    lista_kw, ile_wnisokow, lista_bez_kw, ile_wnioskow_bez_kw = get_lista_kw(df_dzialki)

    wnioski = []
    obciazenia = get_obciazenia(df_obciazenia, df_GDDKIA)
    kw_obicazane_bez_odlaczen = get_obciazenia_bez_odlaczen(
        lista_kw, obciazenia, df_dzialki
    )

    # generowanie kw wpis
    for num, kw in enumerate(lista_kw, start=1):

        print()
        # utwórz wniosek:
        print(f"[{num}/{ile_wnisokow}]", end=" ")
        wniosek = Wniosek(
            "ODL",
            kw["KW"],
            kw["obreb"],
            df_dzialki,
            df_relacje,
            df_osoby,
            df_sady,
            dane_wnioskodawcy,
            df_GDDKIA,
            dzialki_inwestycja,
            kw["jr"],
            obciazenia,
        )
        # utwórz plik pdf z wnioskiem i zalacznikami
        wniosek.dodaj_zalaczniki(
            [
                {
                    "tresc": "DECYZJA WOJEWODY MAZOWIECKIEGO Z DNIA 06.12.2024R. ZNAK: 176/SPEC/2024",
                    "odnosnik": True,
                },
                {"tresc": "PEŁNOMOCNICTWO", "odnosnik": True},
                {
                    "tresc": "WYPIS I WYRYS Z EWIDENCJI GRUNTÓW I BUDYNKÓW",
                    "odnosnik": False,
                },
            ]
        )
        wniosek.print_forms()
        przenies_zalaczniki(df_zalaczniki, wniosek)
        print(f'\nZapis do folderu:"{wniosek.output_path}"')
        wnioski.append(wniosek)

    # generowanie kw zal
    for num, kw in enumerate(lista_bez_kw, start=1):
        print()
        print(f"[{num}/{ile_wnioskow_bez_kw}]", end=" ")
        wniosek = Wniosek(
            "ODL",
            kw["KW"],
            kw["obreb"],
            df_dzialki,
            df_relacje,
            df_osoby,
            df_sady,
            dane_wnioskodawcy,
            df_GDDKIA,
            dzialki_inwestycja,
            kw["jr"],
            obciazenia,
        )
        wniosek.dodaj_zalaczniki(
            [
                {
                    "tresc": "DECYZJA WOJEWODY MAZOWIECKIEGO Z DNIA 06.12.2024R. ZNAK: 176/SPEC/2024",
                    "odnosnik": True,
                },
                {"tresc": "PEŁNOMOCNICTWO", "odnosnik": True},
                {
                    "tresc": "WYPIS I WYRYS Z EWIDENCJI GRUNTÓW I BUDYNKÓW",
                    "odnosnik": False,
                },
                {
                    "tresc": "DOKUMENT POSWIADCZAJACY PRAWO WLASNOSCI DO NIERUCHOMOSCI",
                    "odnosnik": False,
                },
            ]
            + zalaczniki_dokumenty_wlasnosci(wniosek.jr, df_zalaczniki)
        )
        wniosek.print_forms()
        przenies_zalaczniki(df_zalaczniki, wniosek)

        print(f'\nZapis do folderu:"{wniosek.output_path}"')
        wnioski.append(wniosek)

    for num, kw in enumerate(kw_obicazane_bez_odlaczen, start=1):
        print()
        print(f"[{num}/{len(kw_obicazane_bez_odlaczen)}]", end=" ")
        wniosek = Wniosek(
            "OBC",
            kw["KW"],
            kw["obreb"],
            df_dzialki,
            df_relacje,
            df_osoby,
            df_sady,
            dane_wnioskodawcy,
            df_GDDKIA,
            dzialki_inwestycja,
            kw["jr"],
            obciazenia,
        )
        wniosek.dodaj_zalaczniki(
            [
                {
                    "tresc": "DECYZJA WOJEWODY MAZOWIECKIEGO Z DNIA 06.12.2024R. ZNAK: 176/SPEC/2024",
                    "odnosnik": True,
                },
                {"tresc": "PEŁNOMOCNICTWO", "odnosnik": True},
                {
                    "tresc": "WYPIS I WYRYS Z EWIDENCJI GRUNTÓW I BUDYNKÓW",
                    "odnosnik": False,
                },
            ]
        )
        wniosek.print_forms()
        przenies_zalaczniki(df_zalaczniki, wniosek)
        print(f'\nZapis do folderu:"{wniosek.output_path}"')
        wnioski.append(wniosek)

    print("Zakończono tworzenie wniosków")

    save_stats(wnioski)
    merge_wniosek()
    merge_wnioski_obreb()
