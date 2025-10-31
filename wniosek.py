import pandas as pd
from rendering import *
from data_loading import *
from pathlib import Path
from attachments import zalaczniki_dokumenty_wlasnosci
from logger import logger


def krotkie_id(nr_dzialki):
    """wyodrebnij numer dzialki z id dzialki"""
    return nr_dzialki.split(".")[-1]


class Wniosek:
    pierwszy_wniosek = {}
    _counter = 0

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
        jr,
        obciazenia,
    ):
        Wniosek._counter += 1
        self.id = Wniosek._counter

        self.initialize_stats()
        self.tryb = tryb  # "ODL" lub "OBC"
        if (
            KW is None
            or (isinstance(KW, float) and pd.isna(KW))
            or str(KW).strip() == ""
        ):
            self.kw = "BRAK"
        else:
            self.kw = str(KW)
        self.jr = jr
        self.wnioskodawca = dane_wnioskodawcy

        self.find_dzialki(df_dzialki, obreb)
        self.dzialki_odlaczane = self.dzialki_w_inwestycji(dzialki_inwestycja)
        self.obreb = self.ustal_obreb(df_GDDKIA)  # potencjalnie mylące

        self.wlasciciele = []
        self.find_wlasciciele(df_relacje)
        self.ile_wlascicieli = len(self.wlasciciele)
        self.pobierz_dane_wlascicieli(df_wlasciciele)

        self.sad = self.okresl_sad(sady, df_dzialki)

        self.obciazenia = self.find_obciazenia(obciazenia)
        self.okresl_zalaczniki_formularze()
        self.tresc_zadania = self.okresl_tresc_zadania(dzialki_inwestycja)
        self.dzialki_oznaczenia = self.oznaczenie_dzialek(dzialki_inwestycja)

        self.output_path = self.get_output_path()
        if self.kw == "BRAK":
            print(
                f"{str(self.jr).split(".")[-1]} wnioski:",
            )
        else:
            print(
                f"{self.kw} wnioski:",
            )
        logger.info(
            f"ZAINICJALIZOWANO WNIOSEK #{self.id} TRYB:{self.tryb} KW: {self.kw}\n JR: {self.jr}"
        )

    def initialize_stats(self):
        self.stats = {}
        self.stats["formularze"] = []

    def find_dzialki(self, df_dzialki: pd.DataFrame, obreb):
        """znajdz dzialki zrodlowe i projektowane na podstawie nr KW"""
        if self.kw == "BRAK":
            df_kw = df_dzialki[
                (df_dzialki["jr"] == self.jr)
                & (df_dzialki["KW"].isna() | (df_dzialki["KW"] == ""))
            ]
        else:
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
        if not obreby_id:
            return {
                "id": "---",
                "nazwa": "---",
                "gmina": "---",
                "powiat": "---",
            }
        if len(obreby_id) != 1:
            print(
                f"UWAGA:dzialki we wniosku do: {self.kw} znajdują się w dwóch obrebach"
            )

        obreb_id = next(iter(obreby_id))
        obreb_nazwa = df_GDDKIA[df_GDDKIA["obreb_id"] == obreb_id]["obreb"].values[0]
        obreb_gmina = df_GDDKIA[df_GDDKIA["obreb_id"] == obreb_id]["gmina"].values[0]
        obreb_powiat = df_GDDKIA[df_GDDKIA["obreb_id"] == obreb_id]["powiat"].values[0]
        self.kw_docelowa = df_GDDKIA[df_GDDKIA["obreb_id"] == obreb_id][
            "kw_gddkia"
        ].values[0]
        return {
            "id": str(obreb_id),
            "nazwa": obreb_nazwa,
            "gmina": obreb_gmina,
            "powiat": obreb_powiat,
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

    def okresl_sad(self, sady, df_dzialki):
        """Przypisz sąd rejonowy na podstawie numeru kw"""
        if self.kw != "BRAK":
            prefix = self.kw.split("/")[0]
            sad = sady.get(prefix, "-")
        else:
            slownik = self.polacz_obreby_sady(df_dzialki)
            prefix = slownik[self.obreb["id"]]
            sad = sady.get(prefix, "-")
        return sad

    def polacz_obreby_sady(self, df_dzialki):
        # odfiltrowanie pustych KW
        df_dzialki = df_dzialki[
            df_dzialki["KW"].notna() & (df_dzialki["KW"] != "")
        ].copy()

        df_dzialki["teryt_obreb"] = (
            df_dzialki["ID_zrodlowe"].astype(str).str.split(".").str[:2].str.join(".")
        )
        df_dzialki["kod_sadu"] = df_dzialki["KW"].astype(str).str.split("/").str[0]

        result = dict(set(zip(df_dzialki["teryt_obreb"], df_dzialki["kod_sadu"])))

        return result

    def dodaj_zalaczniki(self, zalaczniki_do_dodania: list[dict]):
        """dodaj inne zalaczniki, max 5"""
        zalaczniki_inne = []

        for zalacznik in zalaczniki_do_dodania:
            if zalacznik["odnosnik"] == True:
                tresc = self.odnosnik_do_zalacznika(zalacznik["tresc"])
                zalaczniki_inne.append(tresc)
            else:
                zalaczniki_inne.append(zalacznik["tresc"])
        self.zalaczniki_inne = zalaczniki_inne + ["---"] * (5 - len(zalaczniki_inne))

    def okresl_zalaczniki_formularze(self):

        # utwórz słownik jeżeli jeszcze nie istnieje
        if not hasattr(self, "zalaczniki"):
            self.zalaczniki = {}

        # pelnomocnictwo jest dodawane jako zalacznik lub odnosnik do kazdego wniosku
        self.zalaczniki["kw_pp"] = 1

        # jezeli jest wiecej niz dwoje uczesników (wlascicieli) wpisz liczbe załączników KW-WU
        if self.ile_wlascicieli > 2:
            self.zalaczniki["kw_wu"] = self.ile_wlascicieli - 2
        else:
            self.zalaczniki["kw_wu"] = "---"

        # jezeli jest wiecej niz dwa ograniczenia
        if self.ogr_counter > 2:
            self.zalaczniki["kw_zad"] = 1
        else:
            self.zalaczniki["kw_zad"] = "---"

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
        if self.kw == "BRAK":
            path[3] = self.jr.split(".")[-1]
        return os.path.join(*path)

    def print_forms(self):
        """funkcja wybiera jaki wniosek powinien zostać wygenerowany i przekazuje atrybuty klasy do odpowienich funkcji"""
        output_path = self.output_path

        # jeżeli wniosek jest pierwszym wnioskiem dla swojego obrębu i nie określono docelowej księgi obrębu:

        if (
            self.tryb == "ODL"
            and self.okresl_pierwszy_wniosek()
            and "." in self.kw_docelowa.replace("…", ".")
        ):
            polozenie = self.obreb
            polozenie["dzielnica"] = "---"

            data = {
                "sad": self.sad,
                "kw_odlaczane": self.kw,
                "kw_dolaczane": "-----",
                "polozenie": polozenie,
                "nr_kw": self.kw,
            }

            print_zal(
                self,
                data,
                self.wnioskodawca,
                self.wlasciciele_dane,
                self.zalaczniki,
                self.zalaczniki_inne,
                self.dzialki_oznaczenia,
                output_path,
            )

        # KW-ZAL zalozenie KW poprzez dołączenie jej do KW GDDKIA
        elif self.kw == "BRAK":
            polozenie = self.obreb
            polozenie["dzielnica"] = "---"
            polozenie["wojewodztwo"] = "PODLASKIE"  # do poprawy później
            data = {
                "sad": self.sad,
                "kw_odlaczane": "---",
                "kw_dolaczane": self.kw_docelowa,
                "polozenie": polozenie,
                "nr_kw": self.kw,
            }

            print_zal(
                self,
                data,
                self.wnioskodawca,
                self.wlasciciele_dane,
                self.zalaczniki,
                self.zalaczniki_inne,
                self.dzialki_oznaczenia,
                output_path,
            )

        # KW-WPIS jeżeli wniosek nie jest pierwszym wnioskiem w obrębie lub jest znana księga do której dołącza się działki:
        else:
            data = {
                "sad": self.sad,
                "nr_kw": self.kw,
                "tresc_zadania": self.tresc_zadania,
                "tresc_obciazenia1": self.obciazenia[0],
                "tresc_obciazenia2": self.obciazenia[1],
                "tryb": self.tryb,
            }
            print_wpis(
                self,
                data,
                self.wnioskodawca,
                self.wlasciciele_dane,
                self.zalaczniki,
                self.zalaczniki_inne,
                output_path,
            )
            if self.ogr_counter > 2:
                print_ZAD(self.obciazenia, output_path)

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

    def find_obciazenia(self, obciazenia):
        obciazenia_aktualnej_kw = obciazenia.get(self.kw)
        if not obciazenia_aktualnej_kw:
            self.ogr_counter = 0
            return ["---", "---"]
        elif len(obciazenia_aktualnej_kw) == 1:
            self.ogr_counter = 1
            return [obciazenia_aktualnej_kw[0], "---"]
        else:
            self.ogr_counter = len(obciazenia_aktualnej_kw)
            return obciazenia_aktualnej_kw

    def okresl_tresc_zadania(self, dzialki_inwestycja_wszystkie: dict):
        """Generuje treść żądania dla wnisosku KW-WPIS zawierającą informacje o numerze i powierzchni odłączanych działek"""
        if self.tryb == "OBC":
            return "---"
        if any(
            "GENERALNA" in wlasciciel["nazwa"] for wlasciciel in self.wlasciciele_dane
        ):
            return "---"

        if self.kw != "BRAK":
            tresc = (
                f"WNOSZĘ O BEZOBCIĄŻENIOWE ODŁĄCZENIE Z KSIĘGI WIECZYSTEJ {self.kw} ZGODNIE Z USTAWĄ Z DNIA 10 KWIETNIA"
                ' 2003 R. "O SZCZEGÓLNYCH ZASADACH PRZYGOTOWANIA I REALIZACJI INWESTYCJI W ZAKRESIE DRÓG PUBLICZNYCH" '
                "(DZ.U. 2023 POZ. 162): "
            )

            dzialki_opisy = [
                f"DZIAŁKI NR {krotkie_id(d)} O POW. {dzialki_inwestycja_wszystkie[d]} HA"
                for d in self.dzialki_odlaczane
            ]

            # jeżeli więcej niż jedna działka jest odłączana dodaje "ORAZ przed ostatnim opisem"
            if len(dzialki_opisy) > 1:
                tresc += ", ".join(dzialki_opisy[:-1]) + " ORAZ " + dzialki_opisy[-1]
            else:
                tresc += dzialki_opisy[0]

            if "." in self.kw_docelowa.replace("…", "."):
                kw_do_przylaczenia = f"PIERWSZEJ KSIEGI ZAŁOŻONEJ W OBRĘBIE {self.obreb['nazwa']} W RAMACH INWESTYCJI ZATWIERDZONEJ DECYZJĄ WOJEWODY PODLASKIEGO NR 11/2023 Z DNIA 27.09.2023"
            else:
                kw_do_przylaczenia = f"KSIĘGI {self.kw_docelowa}"

            tresc += (
                f", POŁOŻONEJ W OBREBIE {krotkie_id(self.obreb['id'])} {self.obreb['nazwa']}, GMINA {self.obreb['gmina']}, "
                f"POWIAT {self.obreb['powiat']} I PRZYŁĄCZENIE JEJ DO {kw_do_przylaczenia}."
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
            "path": self.output_path,
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

        path = Path(self.output_path)
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
            "Liczba ograniczen": self.ogr_counter,
            "PATH": self.output_path,
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
