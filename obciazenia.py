import pandas as pd
from data_loading import load_obciazenia
from wniosek import krotkie_id


def get_obciazone_kw(df_obciazenia):
    return df_obciazenia["kw"].dropna().unique()


def stworz_tresc_obicazenia(id_dzialki, kolor: str, tresc_obciazenia, kw):
    id_dzialki = krotkie_id(str(id_dzialki))
    obreb = "SUCHOWOLA"
    koloru = str(kolor).replace("ki", "kiego").replace("ny", "nego").upper()
    tresc_obciazenia = str(tresc_obciazenia).replace(" \n", ", ")
    tresc = f"""
    WNOSZĘ O UJAWNIENIE W DZIALE III KW {kw} OGRANICZENIA SPOSOBU KORZYSTANIA Z NIERUCHOMOŚCI, STANOWIĄCEJ DZIAŁKĘ EW. 
    NR. {id_dzialki} OBR. {obreb} W OBSZARZE OZNACZONYM PRZERYWANĄ LINIĄ KOLORU {koloru} W PROJEKCIE ZAGOSPODAROWANIA TERENU, 
    STANOWIĄCYM CZĘŚĆ ZATWIERDZONEGO DECYZJĄ, PROJEKTU BUDOWLANEGO, POPRZEZ UDZIELENIE GENERALNEMU DYREKTOROWI DRÓG KRAJOWYCH I 
    AUTOSTRAD ZEZWOLENIA NA PROWADZENIE NA WSKAZANEJ WSKAZANEJ CZESCI NIERUCHOMOSCI PRAC ZWIĄZANYCH Z {tresc_obciazenia.upper()}.
    WNOSZĘ O WPISANIE, ŻE WŁAŚCICIEL NIERUCHOMOŚCI JEST ZOBOWIĄZANY DO UDOSTĘPNIENIA OPISANEJ WYŻEJ NIERUCHOMOŚCI NA RZECZ KAŻDOCZESNEGO
    WŁAŚCICIELA SIECI W CELU WYKONANIA CZYNNOŚCI ZWIĄZANYCH Z KONSERWACJĄ ORAZ USUWANIEM AWARII CIĄGÓW, PRZEWODÓW I URZĄDZEŃ NA PODSTAWIE
    OSTATECZNEJ DECYJI WOJEWODY PODLASKIEGO NR. 11/2023 O ZEZWOLENIU NA REALIZACJĘ INWESTYCJI DROGOWEJ Z DNIA 27 WRZEŚNIA 2024. 
    DO OGRANICZEŃ O KTÓRYCH MOWA POWYŻEJ STOSUJE SIĘ ODPOWIEDNIO PRZEPISY ART.P 124 UST. 4-8 I ART. 124A USTAWY Z DNIA 21 SIERPNIA 1997 R.
    O GOSPODARCE NIERUCHOMOŚCIAMI.
    """

    tresc = " ".join(tresc.split())
    return tresc


def polacz_tresc_z_kw(df):
    df["pelna_tresc"] = df.apply(
        lambda row: stworz_tresc_obicazenia(
            row["ID_dzialki"], row["kolor"], row["tresc_obciazenia"], row["kw"]
        ),
        axis=1,
    )
    return df


def agreguj_obciazenia(df):
    wynik = {}
    for kw, grupa in df.groupby("kw"):
        slownik = {
            num: str(pelna_tresc)
            for num, pelna_tresc in enumerate(grupa["pelna_tresc"])
        }
        wynik[kw] = slownik
    return wynik


def print_all_obciazenia(agregowane_obciazenia):
    for kw, tresci in agregowane_obciazenia.items():
        print(f"\nKW: {kw}")
        for num, pelna_tresc in tresci.items():
            print(f"  [{num}] {pelna_tresc}\n")


def get_obciazenia(df_obciazenia: pd.DataFrame):
    df_obciazenia = polacz_tresc_z_kw(df_obciazenia)
    obciazenia_kw = agreguj_obciazenia(df_obciazenia)
    return obciazenia_kw


if __name__ == "__main__":
    print("test")
    obciazenia = load_obciazenia("import/ograniczenia.xlsx")
    obciazenia = polacz_tresc_z_kw(obciazenia)
    obciazenia_kw = agreguj_obciazenia(obciazenia)
    print_all_obciazenia(obciazenia_kw)
