import pandas as pd
from rendering import *
from pathlib import Path


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
    return df_relacje


def nazwisko_zlozone(nazwa):

    nazwisko = nazwa.split()[0]
    if "-" in nazwisko:
        nazwisko = nazwisko.split("-")
        nazwisko1, nazwisko2 = nazwisko[0], nazwisko[1]
    else:
        nazwisko1, nazwisko2 = nazwisko, None
    return nazwisko1, nazwisko2


def poprawny_numer(numer):
    """Sprawdź czy numer pesel, regon, nip == 0, jezeli tak zastap go '---'"""
    if numer == 0 or numer == None:
        numer = "---"
    return numer


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
    return df_osoby


def load_sady(filepath):
    df_excel = pd.read_excel(filepath)
    mapa_sadow = dict(zip(df_excel["kod"], df_excel["sad_rejonowy"]))
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
    return df_GDDKIA


def dzialki_w_inwestycji(df_dzialki):
    """zwroc liste dzialek ktore po podziale znajda sie w inwestycji"""
    df_filtered = df_dzialki[df_dzialki["czy_inwestycja"] == True]
    dzialki = {
        row["ID_projektowane"]: row["powierzchnia"] for _, row in df_filtered.iterrows()
    }
    return dzialki


def krotkie_id(nr_dzialki):
    """wyodrebnij numer dzialki z id dzialki"""
    return nr_dzialki.split(".")[-1]


class Wniosek:
    pierwszy_wniosek = {}

    def __init__(
        self,
        tryb: str,
        KW: str,
        obreb: str,
        df_dzialki: pd.DataFrame,
        df_relacje: pd.DataFrame,
        df_wlasciciele,
        sady: dict,
        dane_wnioskodawcy: dict,
        df_GDDKIA,
        dzialki_inwestycja,
    ):
        self.initialize_stats()
        self.tryb = tryb  # "ODL" lub "OBC"
        self.kw = KW
        self.wnioskodawca = dane_wnioskodawcy

        self.find_dzialki(df_dzialki, obreb)
        self.dzialki_odlaczane = self.dzialki_w_inwestycji(dzialki_inwestycja)
        self.obreb = self.ustal_obreb(
            df_GDDKIA
        )  # potencjalnie mylące - zmienic później

        self.wlasciciele = []
        self.find_wlasciciele(df_relacje)
        self.ile_wlascicieli = len(self.wlasciciele)
        self.pobierz_dane_wlascicieli(df_wlasciciele)

        self.okresl_sad(sady)

        self.okresl_zalaczniki()
        self.tresc_zadania = self.okresl_tresc_zadania(dzialki_inwestycja)
        self.dzialki_oznaczenia = self.oznaczenie_dzialek(dzialki_inwestycja)

        print(f"Wniosek {self.kw} zainicjalizowano")
        print('Zapis do folderu:"', f"{self.get_output_path()}", '" ')

    def initialize_stats(self):
        self.stats = {}
        self.stats["formularze"] = []

    def find_dzialki(self, df_dzialki: pd.DataFrame, obreb):
        """znajdz dzialki zrodlowe i projektowane na podstawie nr KW"""

        # selekcja rekordów z df_dzialki gdzie: kw wnisoku == kw dzialki źródłowej
        df_kw = df_dzialki[df_dzialki["KW"] == self.kw]

        # filtrowanie działek które zaczynają się od numeru obrębu docelowego dla danego wniosku
        df_kw = df_kw[
            df_kw["ID_zrodlowe"].astype(str).str.startswith(obreb)
            | df_kw["ID_projektowane"].astype(str).str.startswith(obreb)
        ]

        # tworzy listę działek źródłowych:
        self.dzialki_zrodlowe = df_kw["ID_zrodlowe"].unique().tolist()
        # tworzy listę działek projektowanych:
        self.dzialki = df_kw["ID_projektowane"].tolist()

        # {dzialka_zrodlowa:[lista_projektowanych]
        self.dzialki_zr_pr = {}
        for _, row in df_kw.iterrows():
            zrodlowa = row["ID_zrodlowe"]
            projektowana = row["ID_projektowane"]
            if pd.notna(zrodlowa) and pd.notna(projektowana):
                self.dzialki_zr_pr.setdefault(zrodlowa, []).append(projektowana)

    def ustal_obreb(self, df_GDDKIA):

        obreby_id = []
        for dzialka in self.dzialki_zrodlowe:
            obreb_id = ".".join(dzialka.split(".")[:2])
            obreby_id.append(obreb_id)

        obreby_id = set(obreby_id)
        if len(obreby_id) == 1:
            obreb_id = next(iter(obreby_id))
            obreb_nazwa = df_GDDKIA[df_GDDKIA["obreb_id"] == obreb_id]["obreb"].values[
                0
            ]
            obreb_gmina = df_GDDKIA[df_GDDKIA["obreb_id"] == obreb_id]["gmina"].values[
                0
            ]
            obreb_powiat = df_GDDKIA[df_GDDKIA["obreb_id"] == obreb_id][
                "powiat"
            ].values[0]
            self.kw_docelowa = df_GDDKIA[df_GDDKIA["obreb_id"] == obreb_id][
                "kw_gddkia"
            ].values[0]

            return {
                "id": str(obreb_id),
                "nazwa": obreb_nazwa,
                "gmina": obreb_gmina,
                "powiat": obreb_powiat,
            }

        print(f"UWAGA:dzialki we wniosku do: {self.kw} znajdują się w dwóch obrebach")
        return {
            "id": "0000",
            "nazwa": "!nieznany",
            "gmina": "!nieznany",
            "powiat": "!nieznany",
        }

    def find_wlasciciele(self, df_relacje):
        """Znajdz id wlascicieli kw na podstawie dzialek"""
        for dzialka in self.dzialki_zrodlowe:
            wlasciciele = df_relacje[df_relacje["ID_dzialki"] == dzialka][
                "ID_wlasciciela"
            ].tolist()
            self.wlasciciele += wlasciciele
        self.wlasciciele = list(set(self.wlasciciele))

    def pobierz_dane_wlascicieli(self, df_wlasiciele: pd.DataFrame):
        self.wlasciciele_dane = []
        for id in self.wlasciciele:
            rekord = df_wlasiciele[df_wlasiciele["ID_osoby"] == id]
            if not rekord.empty:
                self.wlasciciele_dane.append(rekord.iloc[0].to_dict())

    def okresl_sad(self, sady):
        """Przypisz sąd rejonowy na podstawie numeru kw"""
        prefix = self.kw.split("/")[0]
        self.sad = sady.get(prefix, "-")

    def dodaj_zalacznik(self, zalaczniki_do_dodania: list[str]):
        """dodaj inne zalaczniki, max 5"""
        zalaczniki_pola = ["inny1", "inny2", "inny3", "inny4", "inny5"]

        # utwórz słownik jeżeli jeszcze nie istnieje
        if not hasattr(self, "zalaczniki"):
            self.zalaczniki = {}

        zalacznik_index = 0

        # pobierz wartość wg klucza, jeżeli wolna ("---") wstaw załącznik, jeżeli nie, sprawdź następny klucz
        for pole in zalaczniki_pola:
            wartosc = self.zalaczniki.get(pole, "---")
            if wartosc == "---" and zalacznik_index < len(zalaczniki_do_dodania):
                self.zalaczniki[pole] = zalaczniki_do_dodania[zalacznik_index]
                zalacznik_index += 1

        # w pozostale pola wstaw ---
        for pole in zalaczniki_pola:
            if pole not in self.zalaczniki:
                self.zalaczniki[pole] = "---"

        self.okresl_zalaczniki()

    def okresl_zalaczniki(self):
        """
        przygotuj dane do wpisania w Wykazie zalacznikow KW-WPIS/KW-ZAL
        !!! Koniecznie _PO_ dodaniu już wszystkich zalacznikow
        """

        # utwórz słownik jeżeli jeszcze nie istnieje
        if not hasattr(self, "zalaczniki"):
            self.zalaczniki = {}

        # pelnomocnictwo jest dodawane jako zalacznik lub odnosnik do kazdego wniosku
        self.zalaczniki["kw_pp"] = 1

        # jezeli jest wiecej niz dwoje uczesników (wlascicieli) wpisz liczbe załączników KW-WU
        if self.ile_wlascicieli > 2:
            self.zalaczniki["kw_wu"] = self.ile_wlascicieli - 2

        # na kazdym niepustym polu z sekcji inny załącznik wykonaj funkcję odnośnik_do_zalacznika
        # dodany zostanie odnośnik wskazujący w którym wniosku znajduje sie załącznik
        for pole in self.zalaczniki.keys():
            if pole.startswith("inny"):
                if self.zalaczniki[pole] != "---":
                    self.zalaczniki[pole] = self.odnosnik_do_zalacznika(
                        self.zalaczniki[pole]
                    )

    def odnosnik_do_zalacznika(self, zalacznik: str):
        """jezeli wniosek nie jest pierwszym w obrebie, dodaj odnośnik do pierwszego wniosku"""
        if self.okresl_pierwszy_wniosek():
            return zalacznik
        else:
            suffix = (
                f" - znajduje się w aktach {Wniosek.pierwszy_wniosek[self.obreb['id']]}"
            )
            zalacznik += suffix
            return zalacznik

    def okresl_pierwszy_wniosek(self):
        """sprawdza czy jest pierwszym wnioskiem dla obrebu, i zwraca True/False,
        jeżeli nie istnieje pierwszy wnisek, aktualizuje zmienną"""
        pierwszy_wniosek = Wniosek.pierwszy_wniosek.get(self.obreb["id"])

        # jeżeli nie ma infromacji o pierwszym wniosku dla danego obrebu [przechowywanej w klasie] ustal
        # aktualny wniosek jako pierwszy
        if not pierwszy_wniosek:
            Wniosek.pierwszy_wniosek[self.obreb["id"]] = self.kw
            pierwszy_wniosek = self.kw

        if pierwszy_wniosek == self.kw:
            return True
        else:
            return False

    def get_output_path(self):
        """określ ścieżkę zapisu wniosku wg wzoru:
        root\\export\\Sąd_rejonowy_w_{miejscowość}\\{Nazwa obrębu}\\{Nr KW}"""
        path = [
            "export",
            f"Sąd rejonowy {self.sad}".replace(" ", "_"),
            self.obreb["nazwa"],
            self.kw.replace("/", "."),
        ]
        return os.path.join(*path)

    def print_forms(self):
        """funkcja wybiera jaki wniosek powinien zostać wygenerowany i przekazuje atrybuty klasy do odpowienich funkcji"""
        output_path = self.get_output_path()

        # jeżeli wniosek jest pierwszym wnioskiem dla swojego obrębu i nie określono docelowej księgi obrębu:
        if self.okresl_pierwszy_wniosek() and "." in self.kw_docelowa.replace("…", "."):
            polozenie = self.obreb
            polozenie["dzielnica"] = "---"

            data = {
                "sad": self.sad,
                "kw_odlaczane": self.kw,
                "nr_kw": self.kw,
                "polozenie": polozenie,
            }
            print_zal(
                self,
                data,
                self.wnioskodawca,
                self.wlasciciele_dane,
                self.zalaczniki,
                self.dzialki_oznaczenia,
                output_path,
            )
        # jeżeli wniosek nie jest pierwszym wnioskiem w obrębie lub jest znana księga do której dołącza się działki:
        else:
            data = {
                "sad": self.sad,
                "nr_kw": self.kw,
                "tresc_zadania": self.tresc_zadania,
                "tresc_obciazenia": self.okresl_tresc_obciazenia(),
            }
            print_wpis(
                self,
                data,
                self.wnioskodawca,
                self.wlasciciele_dane,
                self.zalaczniki,
                output_path,
            )

    def dzialki_w_inwestycji(self, dzialki_inwestycja_wszystkie):
        """Z listy wszsytkich działek w inwestycji zwraca tylko te których dotyczy wniosek"""
        dzialki_inwestycja = [
            dz for dz in self.dzialki if dz in dzialki_inwestycja_wszystkie
        ]
        self.dzialki_inwestycja = dzialki_inwestycja
        return dzialki_inwestycja

    def oznaczenie_dzialek(self, dzialki_inwestycja_wszystkie: dict) -> list[dict]:
        """generuje listę słowników zawierających oznaczenia działek do formatu wymaganego we wnioskach KW-ZAL i KW-OZN"""
        oznaczenia = []
        for dzialka in self.dzialki_odlaczane:
            oznaczenie = {}
            oznaczenie["ulica"] = "---"
            oznaczenie["id_obrebu"] = (
                f'{krotkie_id(self.obreb["id"])} {self.obreb["nazwa"]}'
            )
            oznaczenie["id_dzialki"] = krotkie_id(dzialka)
            oznaczenie["powierzchnia"] = f"{dzialki_inwestycja_wszystkie[dzialka]} HA"
            oznaczenia.append(oznaczenie)
        return oznaczenia

    def okresl_tresc_obciazenia(self):
        if self.tryb == "OBC":
            tresc = "lorem"
            return tresc
        else:
            return "---"

    def okresl_tresc_zadania(self, dzialki_inwestycja_wszystkie: dict):
        """Generuje treść żądania dla wnisosku KW-WPIS zawierającą informacje o numerze i powierzchni odłączanych działek"""
        if self.tryb == "ODL":
            tresc = (
                f"WNOSZĘ O BEZOBCIĄŻENIOWE ODŁĄCZENIE NIERUCHOMOŚCI Z KSIĘGI WIECZYSTEJ {self.kw} ZGODNIE Z USTAWĄ Z DNIA 10 KWIETNIA"
                ' 2003 R. "O SZCZEGÓLNYCH ZASADACH PRZYGOTOWANIA I REALIZACJI INWESTYCJI W ZAKRESIE DRÓG PUBLICZNYCH" '
                "(DZ.U. 2023 POZ. 162):"
            )

            dzialki_opisy = [
                f"DZIAŁKI NR {krotkie_id(d)} o POW. {dzialki_inwestycja_wszystkie[d]} HA"
                for d in self.dzialki_odlaczane
            ]

            # jeżeli więcej niż jedna działka jest odłączana dodaje "ORAZ przed ostatnim opisem"
            if len(dzialki_opisy) > 1:
                tresc += ", ".join(dzialki_opisy[:-1]) + " ORAZ " + dzialki_opisy[-1]
            else:
                tresc += dzialki_opisy[0]

            tresc += (
                f", POŁOŻONEJ W OBEBIE {krotkie_id(self.obreb['id'])} {self.obreb['nazwa']}, GMINA {self.obreb['gmina']}, "
                f"POWIAT {self.obreb['powiat']} I PRZYŁĄCZENIE JEJ DO KSIĘGI {self.kw_docelowa}."
            )

            # zmiana liczby na mnogą jeżeli konieczne
            if len(self.dzialki_odlaczane) > 1:
                tresc = tresc.replace("POŁOŻONEJ", "POŁOŻONYCH")
                tresc = tresc.replace("JEJ", "ICH")

            return tresc
        else:
            return "---"

    def get_stats(self):
        """Generowanie informacji o danym wniosku, głównie na potrzeby kontroli-debugu, nieużywane w głównej pętli programu"""
        stats = {
            "kw": self.kw,
            "formularze": self.stats["formularze"],
            "liczba_wlascicieli": self.ile_wlascicieli,
            "wlasciciele": [w["nazwa"] for w in self.wlasciciele_dane],
            "ile_dzialek_zrodlowych": len(self.dzialki),
            "ile_dzialek_odlaczanych": len(self.dzialki_odlaczane),
            "dzialki": self.dzialki_zr_pr,
            "zalaczniki": self.zalaczniki,
            "czy_pierwszy_wniosek": self.okresl_pierwszy_wniosek(),
            "path": self.get_output_path(),
        }
        return stats

    def show_stats(self):
        """wyświetla statystyki ze słownika pozyskanego metodą get_stats()"""
        print()
        for key, value in self.get_stats().items():
            if key == "dzialki":
                print("dzialki:")
                for dzialka_zrodlowa, projektowane in value.items():
                    print(f" {dzialka_zrodlowa}:")
                    for p in projektowane:
                        if p in self.dzialki_odlaczane:
                            print(f"  *{p}")
                        else:
                            print(f"   {p}")
            else:
                print(f"{key}: {value}")

    def stats_to_export(self):
        dzialki = ""
        for dzialka in self.dzialki:
            if dzialka in self.dzialki_odlaczane:
                dzialka = f"*{dzialka}"
            dzialki += dzialka + "; "

        path = Path(self.get_output_path())
        relative_path = path.relative_to("export")

        stats_export = {
            "KW": self.kw,
            "Link": f'=HYPERLINK("{relative_path}","LINK")',
            "Formularze": "; ".join(self.stats["formularze"]),
            "KW-ZAL": "1" if "KW-ZAL" in self.stats["formularze"] else "0",
            "KW-WPIS": "1" if "KW-WPIS" in self.stats["formularze"] else "0",
            "KW-WU": "1" if "KW-WU" in self.stats["formularze"] else "0",
            "KW-OZN": "1" if "KW-OZN" in self.stats["formularze"] else "0",
            "Obręb": self.obreb["nazwa"],
            "Czy pierwszy wniosek": self.okresl_pierwszy_wniosek(),
            "Liczba właścicieli": self.ile_wlascicieli,
            "Właściciele": "; ".join(self.wlasciciele),
            "Właściciele N": ". ".join(w["nazwa"] for w in self.wlasciciele_dane),
            "Działki źródłowe": "; ".join(self.dzialki_zrodlowe),
            "Działki projektowane": dzialki,
            "Liczba działek źródłowych": len(self.dzialki_zrodlowe),
            "Liczba działek projektowanych": len(self.dzialki),
            "Liczba działek odłączanych od kw": len(self.dzialki_odlaczane),
            "PATH": self.get_output_path(),
        }

        zalaczniki = {}
        if "kw_pp" in self.zalaczniki.keys():
            zalaczniki["KW-PP"] = self.zalaczniki["kw_pp"]
        if any("decyzja" in str(val).lower() for val in self.zalaczniki.values()):
            zalaczniki["Decyzja"] = 1
        else:
            zalaczniki["Decyzja"] = 0

        stats_export.update(zalaczniki)

        return stats_export
