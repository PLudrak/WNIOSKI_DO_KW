import pandas as pd
import os


def load_data(path="import"):
    """Ładowanie danych o działkach, relacjach, osobach, sądach, księgach gddkia z excela do programu jako DataFrame"""
    df_dzialki = load_dzialki(os.path.join(path, "Dzialki.xlsx"))
    df_relacje = load_relacje(os.path.join(path, "Relacje.xlsx"))
    df_osoby = load_osoby(os.path.join(path, "Wlasciciele.xlsx"))
    df_sady = load_sady(os.path.join(path, "Sady.xlsx"))
    df_GDDKIA = load_gddkia(os.path.join(path, "KW-GDDKIA.xlsx"))
    df_obciazenia = load_obciazenia(os.path.join(path, "ograniczenia.xlsx"))
    dzialki_inwestycja = dzialki_w_inwestycji(df_dzialki)

    return (
        df_dzialki,
        df_relacje,
        df_osoby,
        df_sady,
        df_GDDKIA,
        dzialki_inwestycja,
        df_obciazenia,
    )


def dzialki_w_inwestycji(df_dzialki):
    """zwroc liste dzialek ktore po podziale znajda sie w inwestycji"""
    df_filtered = df_dzialki[df_dzialki["czy_inwestycja"] == True]
    dzialki = {
        row["ID_projektowane"]: row["powierzchnia"] for _, row in df_filtered.iterrows()
    }
    return dzialki


def load_dzialki(filepath):
    # df_dzialki = pd.DataFrame(columns=['ID_zrodlowe','ID_projektowane','powierzchnia','czy_inwestycja','KW'])
    rows = []
    df_excel = pd.read_excel(filepath)

    for _, row in df_excel.iterrows():
        ID_zrodlowe = row["ID_Dzialka"]
        ID_projektowane = row["ID_Projektowane"]
        powierzchnia = row["Powierzchnia"]
        jr = row["J_REJESTR"]

        KW = row["KW"]
        if KW is None:
            KW = "-"

        new_row = {
            "ID_zrodlowe": ID_zrodlowe,
            "ID_projektowane": ID_projektowane,
            "powierzchnia": powierzchnia,
            "czy_inwestycja": row["Inwestycja"],
            "KW": KW,
            "obreb": ".".join(ID_zrodlowe.split(".")[:-1]),
            "jr": jr,
        }
        rows.append(new_row)
    df_dzialki = pd.DataFrame(rows)
    print("Zaladowano informacje o działkach")
    return df_dzialki


def load_relacje(filepath):
    rows = []
    df_excel = pd.read_excel(filepath)

    for _, row in df_excel.iterrows():
        new_row = {
            "ID_wlasciciela": row["ID_Właściciela"],
            "ID_dzialki": row["ID_Działki"],
        }
        rows.append(new_row)

    df_relacje = pd.DataFrame(rows)
    print("Zaladowano informacje o właścicielach")
    return df_relacje


def load_obciazenia(filepath):
    rows = []
    df_excel = pd.read_excel(filepath)
    for _, row in df_excel.iterrows():
        new_row = {
            "kw": row["kw"],
            "ID_dzialki": row["identyfikator_dzialki"],
            "kolor": row["linia_koloru"],
            "tresc_obciazenia": row["tresc_obciazenia"],
        }
        rows.append(new_row)
    df_obciazenia = pd.DataFrame(rows)
    print('Zaladowano informacje o "CZASOWYCH OBCIAZENIACH"')
    return df_obciazenia


def load_osoby(filepath):
    rows = []
    df_excel = pd.read_excel(filepath)

    for _, row in df_excel.iterrows():
        nazwisko, nazwisko2 = nazwisko_zlozone(row["Nazwa_poprawna"])

        # ID_ososby Pesel Regon KRS Nazwa Nazwisko Nazwisko2 Imie1 Imie2 ImieO Imie_m Kraj Miejscowosc Ulica NumerBudnku NumerLokalu KodPocztowy Poczta Pełnomocnik AdresDoreczen
        new_row = {
            "ID_osoby": row["ID_osoby"],
            "pesel": poprawny_numer(row["Pesel"]),
            "regon": poprawny_numer(row["REGON"]),
            "krs": poprawny_numer(row["KRS"]),
            "nazwa": row["Nazwa_poprawna"],
            "nazwisko": nazwisko,
            "nazwisko2": nazwisko2,
            "imie": row["Imie_1"],
            "imie2": row["Imie_2"],
            "imie_ojca": row["Imie_O"],
            "imie_matki": row["Imie_M"],
            "kraj": row["Kraj"],
            "miejscowosc": row["Poczta"],
            "ulica": row["Ulica"],
            "numer_budynku": row["Numer_domu"],
            "numer_lokalu": row["Numer_lokalu"],
            "kod_pocztowy": row["Kod_pocztowy"],
            "poczta": row["Poczta"],
            "pelnomocnik": False,
            "adres_doreczen": False,
            "czy_osoba_prawna": row["osoba"],
        }

        rows.append(new_row)
    df_osoby = pd.DataFrame(rows)
    df_osoby = df_osoby.fillna("-")

    print("Załadowano informacje o osobach")
    return df_osoby


def nazwisko_zlozone(nazwa):
    """funkcja pomocznicza do 'load_osoby(filepath)
    z 'nazwy' osoby wydziela dwa człony nazwiska złożonego lub nazwisko i None w przypadku nazwiska prostego
    """
    nazwisko = nazwa.split()[0]
    if "-" in nazwisko:
        nazwisko = nazwisko.split("-")
        nazwisko1, nazwisko2 = nazwisko[0], nazwisko[1]
    else:
        nazwisko1, nazwisko2 = nazwisko, None
    return nazwisko1, nazwisko2


def poprawny_numer(numer):
    """funkcja pomocznicza do 'load_osoby(filepath)
    Sprawdź czy numer pesel, regon, nip == 0, jezeli tak zastap go '---'"""
    if numer == 0 or numer == None:
        numer = "---"
    return numer


def load_sady(filepath):
    df_excel = pd.read_excel(filepath)
    mapa_sadow = dict(zip(df_excel["kod"], df_excel["sad_rejonowy"]))

    print("Załadowano informacje o sądach")
    return mapa_sadow


def load_gddkia(filepath):
    df_excel = pd.read_excel(filepath)
    rows = []
    for _, row in df_excel.iterrows():
        new_row = {
            "obreb": row["OBREB"],
            "obreb_id": row["obreb_id"],
            "kw_gddkia": row["KW GDDK"],
            "gmina": row["GMINA"],
            "powiat": row["POWIAT"],
            "wojewodztwo": row["WOJEWODZTWO"],
        }

        rows.append(new_row)
    df_GDDKIA = pd.DataFrame(rows)
    print("Załadowano informacje o Księgach GDDKIA i obrębach")
    return df_GDDKIA
