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
	#print(df_dzialki.head())
	df_relacje = load_relacje(r"import/Relacje.xlsx")
	#print(df_relacje.head())
	df_osoby = load_osoby(r"import/Wlasciciele.xlsx")
	#print(df_osoby.head())
	df_sady = load_sady(r"import/Sady.xlsx")
	lista_kw = ["RA1L/00034474/9","RA1L/00062793/6","RA1L/00023185/6"]
	wnioski = []

	for kw in lista_kw:
		wnioski.append(Wniosek(kw,df_dzialki,df_relacje,df_osoby,df_sady,dane_wnioskodawcy))
	print()

	wnioski[0].print_forms()