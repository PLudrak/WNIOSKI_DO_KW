import pandas as pd
import os
from wniosek import *
import shutil


def przenies_zalaczniki(df_zalaczniki, wniosek: "Wniosek"):
    path = ["import", "zalaczniki"]
    for zalacznik in wniosek.zalaczniki_inne:
        if "znajduje się w aktach" not in zalacznik:
            if file := get_filename_zalacznik(zalacznik, df_zalaczniki):
                org_path = os.path.join(*path, file)
                print(org_path)
                new_path = os.path.join(wniosek.output_path, file)
                try:
                    shutil.copy2(org_path, new_path)
                    PDFRegistry.add(new_path)
                except:
                    print(f'Nie znaleziono pliku "{file}"')


def get_filename_zalacznik(zalacznik: str, df_zalaczniki):

    filename = pd.Series(
        df_zalaczniki.loc[df_zalaczniki["dokument"] == zalacznik, "file"]
    )
    if zalacznik != "---" and not filename.empty:
        return filename.iloc[0]
    elif zalacznik != "---" and "WYRYS" not in zalacznik.upper():
        print(f"Nie znaleziono pliku załącznika: {zalacznik}")
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
