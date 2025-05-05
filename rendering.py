from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from pdf_handling import PDFRegistry
import os


def load_template(template_name: str):
    """ładuje template z folderami bazowymi //forms i //static"""
    env = Environment(loader=FileSystemLoader(["forms", "static"]))
    return env.get_template(template_name)


def rozdziel_uczestnikow(wlasciciele: list[dict]):
    """
    Rozdzila listę uczestników na na uczestnika pierwszego, drugiego i pozostałych.
    We wnisoku jest miejsce na dwóch uczestników postępowania, pozostali są dodawaniu we załączniku KW-WU

    Args:
        wlasciciele (list[dict]): Lista słowników zawierająca dane o właścicielach

    Returns:
        tuple(dict,dict,list[dict]):
            - słownik z danymi pierwszego uczestnika
            - słownik z dnaymi drugiego uczestnika (może być pusty)
            - lista pozostałych uczestników (może być pusta)
    """
    uczestnik1 = wlasciciele[0] if len(wlasciciele) > 0 else {}
    uczestnik2 = wlasciciele[1] if len(wlasciciele) > 1 else {}
    pozostali = wlasciciele[2:] if len(wlasciciele) > 2 else []
    return uczestnik1, uczestnik2, pozostali


def rozdziel_dzialki(dzialki: list[dict]):
    """
    Dzieli listę działek na pierwszą i pozostałe.

    Zwraca pierwszy element jako osobny słownik oraz listę pozostałych.
    Jeśli lista jest pusta, zwraca pusty słownik i pustą listę.
    """
    # Pierwsza działka lub pusty słownik, jeśli lista pusta
    dzialka = dzialki[0] if len(dzialki) > 0 else {}
    # Reszta działek lub pusta lista
    pozostale = dzialki[1:] if len(dzialki) > 1 else []
    return dzialka, pozostale


def zeruj_slownik(my_dict):
    """Zwraca słownik utworzony na podstawie innego słownika,
    zastępując wszystkie wartosci znakami --- na potrzeby wyswietlania w formularzu"""
    new_dict = dict.fromkeys(my_dict.keys(), "---")
    return new_dict


def wlasciciele_do_druku(wlasciciele: list[dict]):
    """Przygotowuje dane wlascicielu do druku"""
    wlasciciele_poprawione = []

    # jeżeli właścicielem jest osoba prawna zamien nazwisko na pelna nazwe w celu
    # poprawnego wyswietlenia we wniosku

    for wlasciciel in wlasciciele:
        if wlasciciel["czy_osoba_prawna"]:
            wlasciciel["nazwisko"] = wlasciciel["nazwa"]
        wlasciciele_poprawione.append(wlasciciel)

    uczestnik1, uczestnik2, pozostali_uczestnicy = rozdziel_uczestnikow(wlasciciele)

    # jeżeli jest jeden właściciel skreśl pozostałe pola w formularzu
    if len(wlasciciele) == 1:
        uczestnik2 = zeruj_slownik(uczestnik1)
    return uczestnik1, uczestnik2, pozostali_uczestnicy


def print_zal(wniosek, data, wnioskodawca, wlasciciele, zalaczniki, dzialki, path):
    base_path = os.path.abspath("forms")
    output_path = os.path.join(path, "KW-ZAL.pdf")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    u1, u2, pozostali_uczestnicy = wlasciciele_do_druku(wlasciciele)
    template = load_template("KW-ZAL_1.html")
    dzialka, pozostale_dzialki = rozdziel_dzialki(dzialki)
    html = template.render(
        **data,
        zalaczniki=zalaczniki,
        wnioskodawca=wnioskodawca,
        oznaczenie=dzialka,
        uczestnik=u1,
        uczestnik2=u2,
    )
    save_pdf(html, output_path, base_path)
    print("KW-ZAL - zapisano")
    wniosek.stats["formularze"].append("KW-ZAL")
    if pozostali_uczestnicy:
        print_WU(pozostali_uczestnicy, path)
        wniosek.stats["formularze"].append("KW-WU")
    if pozostale_dzialki:
        print_OZN(pozostale_dzialki, data["nr_kw"], path)
        wniosek.stats["formularze"].append("KW-OZN")


def print_OZN(dzialki, kw, path):
    base_path = os.path.abspath("forms")
    output_path = os.path.join(path, "KW-OZN.pdf")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    for num, dzialka in enumerate(dzialki, start=2):
        dzialka["lp"] = num
        dzialka["kw"] = kw

    template = load_template("KW-OZN.html")
    html = template.render(oznaczenia=dzialki)
    save_pdf(html, output_path, base_path)
    print("KW-OZN - zapisano")


def print_wpis(wniosek, data, wnioskodawca, wlasciciele, zalaczniki, path):
    base_path = os.path.abspath("forms")
    output_path = os.path.join(path, "KW-WPIS.pdf")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    u1, u2, pozostali_uczestnicy = wlasciciele_do_druku(wlasciciele)

    strony = [
        ("KW-WPIS_1.html", {"numer_strony": "1"}),
        ("KW-WPIS_2.html", {"numer_strony": "2"}),
        (
            "KW-WPIS_3.html",
            {"numer_strony": "3", "uczestnik": u1, "wnioskodawca": wnioskodawca},
        ),
        (
            "KW-WPIS_4.html",
            {"numer_strony": "4", "uczestnik": u2, "zalaczniki": zalaczniki},
        ),
    ]
    rendered_pages = []

    for template_name, context in strony:
        template = load_template(template_name)
        html = template.render(**data, **context)
        rendered_pages.append(html)

    combined_html = "".join(rendered_pages)

    while True:
        try:
            save_pdf(combined_html, output_path, base_path)
            print("KW-WPIS - zapisano")
            wniosek.stats["formularze"].append("KW-WPIS")
            if pozostali_uczestnicy:
                print_WU(pozostali_uczestnicy, path)
                wniosek.stats["formularze"].append("KW-WU")
            break
        except Exception:
            print("Spróbować ponownie? (T/N)")
            odp = input().strip().lower()
            if odp != "t":
                print("Zapis przerwany.")
                break


def print_WU(uczestnicy, path):

    base_path = os.path.abspath("forms")
    output_path = os.path.join(path, "KW-WU.pdf")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rendered_pages = []

    for i, uczestnik in enumerate(uczestnicy, start=1):
        context = {"numer_strony": str(i), "uczestnik": uczestnik}
        template = load_template("KW-WU.html")
        html = template.render(**context)
        rendered_pages.append(html)

    combined_html = "".join(rendered_pages)

    try:
        save_pdf(combined_html, output_path, base_path)
        print(f"KW-WU - zapisano")
    except Exception as e:
        print(f"[!] KW-WU - błąd zapisu {e}")
        raise


def save_pdf(html_string: str, output_path: str, base_url: str):
    try:
        HTML(string=html_string, base_url=base_url).write_pdf(output_path)
        PDFRegistry.add(output_path)
    except Exception as e:
        print(f"Błąd zapisu: {e}")
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception as remove_error:
            print(f"Nie udało się usunąć uszkodzonego pliku: {remove_error}")
        raise  # ponowne wyrzucenie błędu, żeby móc obsłużyć wyżej
