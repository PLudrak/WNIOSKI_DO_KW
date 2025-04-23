import pandas as pd

def load_dzialki(filepath):
	#df_dzialki = pd.DataFrame(columns=['ID_zrodlowe','ID_projektowane','powierzchnia','czy_inwestycja','KW'])
	rows = []
	df_excel = pd.read_excel(filepath)

	for _,row in df_excel.iterrows():
		ID_zrodlowe = row['ID_Dzialka']
		ID_projektowane = row['ID_Projektowane']
		powierzchnia = row['Powierzchnia']
		
		if type(row['Inwestycja'])== str and row['Inwestycja'].upper() == "PRAWDA":
			czy_inwestycja = True
		else: 
			czy_inwestycja = False
		
		KW = row['KW']
		if KW is None:
			KW = '-'
		
		new_row ={
			'ID_zrodlowe':ID_zrodlowe,
			'ID_projektowane':ID_projektowane,
			'powierzchnia': powierzchnia,
			'czy_inwestycja':czy_inwestycja,
			'KW':KW
		}
		rows.append(new_row)
	df_dzialki = pd.DataFrame(rows)
	return df_dzialki

def load_relacje(filepath):
	rows=[]
	df_excel= pd.read_excel(filepath)

	for _,row in df_excel.iterrows():
		new_row = {'ID_wlasciciela':row['ID_Właściciela'],'ID_dzialki':row['ID_Działki']}
		rows.append(new_row)

	df_relacje = pd.DataFrame(rows)		
	return df_relacje

def load_osoby(filepath):
	rows=[]
	df_excel = pd.read_excel(filepath)

	for _,row in df_excel.iterrows():
		#ID_ososby Pesel Regon KRS Nazwa Nazwisko Nazwisko2 Imie1 Imie2 ImieO Imie_m Kraj Miejscowosc Ulica NumerBudnku NumerLokalu KodPocztowy Poczta Pełnomocnik AdresDoreczen
		new_row ={
			'ID_osoby':row['ID_osoby'],
			'pesel':row['Pesel'],
			'regon':row['REGON'],
			'krs':row['KRS'],
			'nazwa':row['Nazwa_poprawna'],
			'nazwisko':row['Nazwa_poprawna'].split()[0],
			'imie':row['Imie_1'],
			'imie2':row['Imie_2'],
			'imie_ojca':row['Imie_O'],
			'imie_matki':row['Imie_M'],
			'kraj':row['Kraj'],
			'mijescowosc':row['Poczta'],
			'ulica':row['Ulica'],
			'numer_budynku':row['Numer_domu'],
			'numer_lokalu':row['Numer_lokalu'],
			'kod_pocztowy':row['Kod_pocztowy'],
			'poczta':row['Poczta'],
			'pelnomocnik' : False,
			'adres_doreczen' :False
		}
		rows.append(new_row)
	df_osoby=pd.DataFrame(rows)
	df_osoby=df_osoby.fillna("-")
	return df_osoby

class Wniosek:
	
	def __init__ (self,KW:str,df_dzialki:pd.DataFrame,df_relacje:pd.DataFrame):
		self.kw =KW
		print(f"Wniosek {self.kw} zainicjalizowano")
		self.wlasciciele = []
		self.find_dzialki(df_dzialki)
		self.find_wlasciciele(df_relacje)
	
	def find_dzialki(self,df_dzialki:pd.DataFrame):
		"""znajdz dzialki zrodlowe i projektowane na podstawie nr KW"""
		
		#selekcja rekordów z df_dzialki gdzie: kw wnisoku == kw dzialki źródłowej
		df_kw = df_dzialki[df_dzialki['KW'] == self.kw]

		#tworzy listę działek źródłowych:
		self.dzialki_zrodlowe = df_kw['ID_zrodlowe'].unique().tolist()
		#tworzy listę działek projektowanych:
		self.dzialki = df_kw['ID_projektowane'].tolist()
		
		#{dzialka_zrodlowa:[lista_projektowanych]
		self.dzialki_zr_pr = {}
		for _, row in df_kw.iterrows():
			zrodlowa = row['ID_zrodlowe']
			projektowana = row['ID_projektowane']
			if pd.notna(zrodlowa) and pd.notna(projektowana):
				self.dzialki_zr_pr.setdefault(zrodlowa,[]).append(projektowana)

		print(self.dzialki_zr_pr)
	
	def find_wlasciciele(self,df_relacje):
		"""Znajdz id wlascicieli kw na podstawie dzialek"""
		for dzialka in self.dzialki_zrodlowe:
			wlasciciele = df_relacje[df_relacje['ID_dzialki']==dzialka]['ID_wlasciciela'].tolist()
			self.wlasciciele += wlasciciele
		self.wlasciciele= list(set(self.dzialki))
		print(wlasciciele)