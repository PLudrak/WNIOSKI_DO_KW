import pandas as pd
import os
from wniosek import *
import shutil
from logger import logger, shorten_back, shorten_front


def przenies_zalaczniki(df_zalaczniki, wniosek: "Wniosek"):
    logger.info(f"Wniosek: {wniosek.kw} Przenoszenie załączników")
    path = ["import", "zalaczniki"]
    przenies_kwpp(path, wniosek)

    for zalacznik in wniosek.zalaczniki_inne:
        if "znajduje się w aktach" not in zalacznik:
            if file := get_filename_zalacznik(zalacznik, df_zalaczniki):
                org_path = os.path.join(*path, file)
                new_path = os.path.join(wniosek.output_path, file)
                try:
                    shutil.copy2(org_path, new_path)
                    PDFRegistry.add(new_path)
                    logger.info(
                        f"Plik '{shorten_front(org_path)}' przeniesiono do {shorten_front(new_path)}"
                    )
                except:
                    logger.error(f'Nie znaleziono pliku "{shorten_back(file)}"')


def przenies_kwpp(path, wniosek):
    file = "KW-PP.pdf"
    org_path = os.path.join(*path, file)
    new_path = os.path.join(wniosek.output_path, file)
    try:
        shutil.copy2(org_path, new_path)
        PDFRegistry.add(new_path)
        logger.info(
            f"Plik {shorten_front(org_path)} przeniesiono do {shorten_front(new_path)}"
        )
    except:
        logger.error(f'Nie znaleziono pliku "{shorten_back(file)}"')


def get_filename_zalacznik(zalacznik: str, df_zalaczniki):

    filename = pd.Series(
        df_zalaczniki.loc[df_zalaczniki["dokument"] == zalacznik, "file"]
    )
    if zalacznik != "---" and not filename.empty:
        return filename.iloc[0]
    elif zalacznik != "---" and "WYRYS" not in zalacznik.upper():
        logger.warning(
            f"Brak załącznika w tabeli 'ZALACZNIKI.xlsx : {shorten_back(zalacznik)}"
        )
    else:
        return None


def zalaczniki_dokumenty_wlasnosci(jr, df_zalaczniki: pd.DataFrame):
    dokumenty = pd.Series(
        df_zalaczniki.loc[df_zalaczniki["jr"] == jr, "dokument"]
    ).tolist()
    zalaczniki = []
    for dokument in dokumenty:
        zalacznik = {"tresc": dokument, "odnosnik": False}
        zalaczniki.append(zalacznik)

    return zalaczniki
