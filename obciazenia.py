import re
import pandas as pd
from data_loading import load_obciazenia
from wniosek import krotkie_id


def get_obciazone_kw(df_obciazenia):
    return df_obciazenia["kw"].dropna().unique()


def usun_spacje_przed_znakami(text):
    # Usuwa spacje przed przecinkami i kropkami
    text = re.sub(r"\s+([,.])", r"\1", text)
    # Opcjonalnie – usuń podwójne spacje
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def popraw_przypadek_obciazenia(tresc_obciazenia: str) -> str:
    zmiany = {"PRZEBUDOWA": "PRZEBUDOWĄ", "BUDOWA": "BUDOWĄ", "ROZBIÓRKA": "ROZBIÓRKĄ"}
    for slowo, forma in zmiany.items():
        tresc_obciazenia = tresc_obciazenia.replace(slowo, forma)
    return tresc_obciazenia


def popraw_tresc_obciazenia(tresc_obciazenia: str) -> str:
    tresc_obciazenia = popraw_przypadek_obciazenia(tresc_obciazenia.upper())
    tresc_obciazenia = str(tresc_obciazenia).replace(" \n", ", ")
    tresc_obciazenia = usun_spacje_przed_znakami(tresc_obciazenia)

    return tresc_obciazenia


def stworz_tresc_obicazenia(id_dzialki, kolor: str, tresc_obciazenia, kw, obreb):
    tresc_obciazenia = popraw_tresc_obciazenia(tresc_obciazenia)
    id_dzialki = krotkie_id(str(id_dzialki))
    koloru = str(kolor).replace("ki", "kiego").replace("wy", "wego").upper()
    tresc = f"""
    WNOSZĘ O UJAWNIENIE W DZIALE III KW {kw} OGRANICZENIA SPOSOBU KORZYSTANIA Z NIERUCHOMOŚCI, STANOWIĄCEJ DZIAŁKĘ EW. 
    NR. {id_dzialki} OBR. {obreb} W OBSZARZE OZNACZONYM PRZERYWANĄ LINIĄ KOLORU {koloru} W PROJEKCIE ZAGOSPODAROWANIA TERENU, 
    STANOWIĄCYM CZĘŚĆ ZATWIERDZONEGO DECYZJĄ, PROJEKTU BUDOWLANEGO, POPRZEZ UDZIELENIE GENERALNEMU DYREKTOROWI DRÓG KRAJOWYCH I 
    AUTOSTRAD ZEZWOLENIA NA PROWADZENIE NA WSKAZANEJ CZESCI NIERUCHOMOSCI PRAC ZWIĄZANYCH Z {tresc_obciazenia}.
    WNOSZĘ O WPISANIE, ŻE WŁAŚCICIEL NIERUCHOMOŚCI JEST ZOBOWIĄZANY DO UDOSTĘPNIENIA OPISANEJ WYŻEJ NIERUCHOMOŚCI NA RZECZ KAŻDOCZESNEGO
    WŁAŚCICIELA SIECI W CELU WYKONANIA CZYNNOŚCI ZWIĄZANYCH Z KONSERWACJĄ ORAZ USUWANIEM AWARII CIĄGÓW, PRZEWODÓW I URZĄDZEŃ NA PODSTAWIE
    OSTATECZNEJ DECYJI WOJEWODY PODLASKIEGO NR. 11/2023 O ZEZWOLENIU NA REALIZACJĘ INWESTYCJI DROGOWEJ Z DNIA 27 WRZEŚNIA 2024. 
    DO OGRANICZEŃ O KTÓRYCH MOWA POWYŻEJ STOSUJE SIĘ ODPOWIEDNIO PRZEPISY ART.124 UST. 4-8 I ART. 124A USTAWY Z DNIA 21 SIERPNIA 1997 R.
    O GOSPODARCE NIERUCHOMOŚCIAMI.
    """

    tresc = " ".join(tresc.split())
    return tresc


def okresl_obreb_obciazenia(df_obciazenia, df_GDDKIA):
    df_GDDKIA["obreb_id"] = df_GDDKIA["obreb_id"].astype(str)
    df_obciazenia["ID_dzialki"] = df_obciazenia["ID_dzialki"].astype(str)

    df_obciazenia["obreb_id"] = df_obciazenia["ID_dzialki"].str[:13]
    df_out = df_obciazenia.merge(df_GDDKIA, on="obreb_id", how="left")
    return df_out


def polacz_tresc_z_kw(df, df_gddkia):
    df = okresl_obreb_obciazenia(df, df_gddkia)
    df["pelna_tresc"] = df.apply(
        lambda row: stworz_tresc_obicazenia(
            row["ID_dzialki"],
            row["kolor"],
            row["tresc_obciazenia"],
            row["kw"],
            row["obreb"],
        ),
        axis=1,
    )
    return df


def agreguj_obciazenia(df):
    wynik = {}
    for kw, grupa in df.groupby("kw"):
        lista_tresci = [str(tresc) for tresc in grupa["pelna_tresc"]]
        wynik[kw] = lista_tresci
    return wynik


def print_all_obciazenia(agregowane_obciazenia):
    for kw, tresci in agregowane_obciazenia.items():
        print(f"\nKW: {kw}")
        for num, pelna_tresc in tresci.items():
            print(f"  [{num}] {pelna_tresc}\n")


def get_obciazenia(df_obciazenia: pd.DataFrame, df_gddkia):
    df_obciazenia = polacz_tresc_z_kw(df_obciazenia, df_gddkia)
    obciazenia_kw = agreguj_obciazenia(df_obciazenia)
    return obciazenia_kw


def get_obciazenia_bez_odlaczen(lista_kw, obciazenia, df_dzialki):
    """
    Zwracan listę słowników {KW, obreb, jr} dla KW z obciążeń, które nie są na liście KW z inwestycji
    """
    obciazenia_bez_odlaczen = []
    lista_nr_kw = [item["KW"] for item in lista_kw]

    for kw in obciazenia.keys():
        if not kw or str(kw).strip() == "" or str(kw) == "nan":
            continue

        if kw not in lista_nr_kw:
            # wyszukiwanie info o obrebie i jr na podstawie pierwszej dzialki w KW
            # print(kw)
            rekord = df_dzialki[df_dzialki["KW"] == kw]

            if not rekord.empty:
                obreb = rekord.iloc[0]["obreb"]
                jr = rekord.iloc[0]["jr"]
            else:
                obreb = "---"
                jr = "---"
            obciazenia_bez_odlaczen.append({"KW": kw, "obreb": obreb, "jr": jr})
    print(f"\nKsiegi do obiciazenia spoza inwestycji [{len(obciazenia_bez_odlaczen)}]:")
    for line in obciazenia_bez_odlaczen:
        print(line)
    return obciazenia_bez_odlaczen
