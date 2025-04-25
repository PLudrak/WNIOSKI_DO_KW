import pandas as pd
from functions import *
from rendering import *
#Zaladuj dzialki i kw

dane_wnioskodawcy = {
	"pesel":"----------",
	"regon":"017511575",
	"krs":"-"*10,
	"nazwa":"SKARB PAŃSTWA - GENERALNY DYREKTOR DRÓG KRAJOWYCH I AUTOSTRAD",
	"nazwisko2":"-"*10,
	"imie":"-"*10,
	"imie2":"-"*10,
	"imie_ojca":"-"*10,
	"imie_matki":"-"*10,
	"kraj":"POLSKA",
	"miejscowosc":"WARSZAWA",
	"ulica":"Wronia",
	"nr_budynku":"53",
	"nr_lokalu":"---",
	"kod_pocztowy":"00-874"
}

if __name__=='__main__':
	df_dzialki = load_dzialki(r"import/Dzialki.xlsx")
	print("Zaladowano informacje o działkacj")
	print(df_dzialki.head())
	df_relacje = load_relacje(r"import/Relacje.xlsx")
	print("Zaladowano informacje o właścicielach")
	df_osoby = load_osoby(r"import/Wlasciciele.xlsx")
	print("Załadowano informacje o osobach")
	df_sady = load_sady(r"import/Sady.xlsx")
	print("Załadowano informacje o sądach")
	df_GDDKIA = load_gddkia(r"import/KW-GDDKIA.xlsx")
	print("Załadowano informacje o Księgach GDDKIA i obrębach")
	dzialki_inwestycja = dzialki_w_inwestycji(df_dzialki)

	

	lista_kw = sorted(
		df_dzialki[df_dzialki["czy_inwestycja"]==True][['KW','obreb']]
		.dropna()
		.drop_duplicates()
		.to_dict(orient='records'),
		key=lambda x: x['KW']
	)
	for line in lista_kw:
		print(line["KW"], line["obreb"])
	wnioski = []
	for kw in lista_kw:
		wniosek = Wniosek(kw['KW'],kw['obreb'],df_dzialki,df_relacje,df_osoby,df_sady,dane_wnioskodawcy,df_GDDKIA, dzialki_inwestycja)
		wniosek.print_forms()
		wnioski.append(wniosek)
	
