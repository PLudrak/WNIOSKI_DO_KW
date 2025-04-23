import pandas as pd
from functions import *

#Zaladuj dzialki i kw


if __name__=='__main__':
	df_dzialki = load_dzialki(r"import/Dzialki.xlsx")
	#print(df_dzialki.head())
	df_relacje = load_relacje(r"import/Relacje.xlsx")
	#print(df_relacje.head())
	df_osoby = load_osoby(r"import/Wlasciciele.xlsx")
	#print(df_osoby.head())

	lista_kw = ["RA1L/00034474/9","RA1L/00062793/6","RA1L/00023185/6"]
	for kw in lista_kw:
		Wniosek(kw,df_dzialki,df_relacje)
