import pandas as pd
from rendering import *

def load_dzialki(filepath):
	#df_dzialki = pd.DataFrame(columns=['ID_zrodlowe','ID_projektowane','powierzchnia','czy_inwestycja','KW'])
	rows = []
	df_excel = pd.read_excel(filepath)

	for _,row in df_excel.iterrows():
		ID_zrodlowe = row['ID_Dzialka']
		ID_projektowane = row['ID_Projektowane']
		powierzchnia = row['Powierzchnia']
		
		
		KW = row['KW']
		if KW is None:
			KW = '-'
		
		new_row ={
			'ID_zrodlowe':ID_zrodlowe,
			'ID_projektowane':ID_projektowane,
			'powierzchnia': powierzchnia,
			'czy_inwestycja':row["Inwestycja"],
			'KW':KW,
			'obreb': ".".join(ID_zrodlowe.split(".")[:-1])
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

def nazwisko_zlozone(nazwa):
	
	nazwisko = nazwa.split()[0]
	if "-" in nazwisko:
		nazwisko = nazwisko.split("-")
		nazwisko1,nazwisko2 = nazwisko [0],nazwisko[1]
	else:
		nazwisko1,nazwisko2 = nazwisko, None
	return nazwisko1, nazwisko2

def poprawny_numer(numer):
	"""Sprawdź czy numer pesel, regon, nip == 0, jezeli tak zastap go '---' """
	if numer == 0 or numer == None:
		numer = "---"
	return numer

def load_osoby(filepath):
	rows=[]
	df_excel = pd.read_excel(filepath)

	for _,row in df_excel.iterrows():
		nazwisko,nazwisko2 = nazwisko_zlozone(row['Nazwa_poprawna'])

		#ID_ososby Pesel Regon KRS Nazwa Nazwisko Nazwisko2 Imie1 Imie2 ImieO Imie_m Kraj Miejscowosc Ulica NumerBudnku NumerLokalu KodPocztowy Poczta Pełnomocnik AdresDoreczen
		new_row ={
			'ID_osoby':row['ID_osoby'],
			'pesel':poprawny_numer(row['Pesel']),
			'regon':poprawny_numer(row['REGON']),
			'krs':poprawny_numer(row['KRS']),
			'nazwa':row['Nazwa_poprawna'],
			'nazwisko':nazwisko,
			'nazwisko2':nazwisko2,
			'imie':row['Imie_1'],
			'imie2':row['Imie_2'],
			'imie_ojca':row['Imie_O'],
			'imie_matki':row['Imie_M'],
			'kraj':row['Kraj'],
			'miejscowosc':row['Poczta'],
			'ulica':row['Ulica'],
			'numer_budynku':row['Numer_domu'],
			'numer_lokalu':row['Numer_lokalu'],
			'kod_pocztowy':row['Kod_pocztowy'],
			'poczta':row['Poczta'],
			'pelnomocnik' : False,
			'adres_doreczen' :False,
			'czy_osoba_prawna':row['osoba']
		}


		rows.append(new_row)
	df_osoby=pd.DataFrame(rows)
	df_osoby=df_osoby.fillna("-")
	return df_osoby

def load_sady(filepath):
	df_excel=pd.read_excel(filepath)
	mapa_sadow = dict(zip(df_excel['kod'], df_excel['sad_rejonowy']))
	return mapa_sadow

def load_gddkia(filepath):
	df_excel=pd.read_excel(filepath)
	rows = []
	for _,row in df_excel.iterrows():
		new_row = {
			"obreb":row["OBREB"],
			"obreb_id":row["obreb_id"],
			"kw_gddkia":row["KW GDDK"],
			"gmina": row["GMINA"],
			"powiat": row["POWIAT"]}

		rows.append(new_row)
	df_GDDKIA = pd.DataFrame(rows)
	return df_GDDKIA

def dzialki_w_inwestycji(df_dzialki):
	"""zwroc liste dzialek ktore po podziale znajda sie w inwestycji"""
	df_filtered = df_dzialki[df_dzialki["czy_inwestycja"]==True]
	dzialki ={
		row["ID_projektowane"]:row["powierzchnia"]
		for _, row in df_filtered.iterrows()
	}
	return dzialki
	

def krotkie_id(nr_dzialki):
	"""wyodrebnij numer dzialki z id dzialki"""
	return nr_dzialki.split(".")[-1]

class Wniosek:
	pierwszy_wniosek= {}

	def __init__ (self,KW:str,obreb:str,df_dzialki:pd.DataFrame,df_relacje:pd.DataFrame,df_wlasciciele,sady:dict,dane_wnioskodawcy:dict,df_GDDKIA, dzialki_inwestycja):
		self.kw =KW
		self.wlasciciele = []
		self.wlasciciele_dane = []
		self.dzialki_zrodlowe = []
		self.dzialki_zr_pr = []
		self.formularze = ['KW-WPIS']
		self.sad = []
		self.wnioskodawca = dane_wnioskodawcy
		self.zalaczniki = []
		self.find_dzialki(df_dzialki,obreb)
		self.obreb = self.ustal_obreb(df_GDDKIA) #potencjalnie mylące - zmienic później
		self.find_wlasciciele(df_relacje)
		self.ile_wlascicieli = len(self.wlasciciele)
		self.pobierz_dane_wlascicieli(df_wlasciciele)
		self.okresl_sad(sady)
		self.okresl_zalaczniki()
		self.tresc_zadania = self.okresl_tresc_zadania(dzialki_inwestycja)
		
		print(f"\nWniosek {self.kw} zainicjalizowano")
		print(f'Zapis do folderu:" {self.get_output_path()}"')

	def find_dzialki(self,df_dzialki:pd.DataFrame,obreb):
		"""znajdz dzialki zrodlowe i projektowane na podstawie nr KW"""
		
		#selekcja rekordów z df_dzialki gdzie: kw wnisoku == kw dzialki źródłowej
		df_kw = df_dzialki[df_dzialki['KW'] == self.kw]

		#filtrowanie działek które zaczynają się od numeru obrębu docelowego dla danego wniosku
		df_kw = df_kw[
			df_kw['ID_zrodlowe'].astype(str).str.startswith(obreb) |
			df_kw['ID_projektowane'].astype(str).str.startswith(obreb)
		]


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

	def ustal_obreb(self,df_GDDKIA):
		
		obreby_id =[]
		for dzialka in self.dzialki_zrodlowe:
			obreb_id = ".".join(dzialka.split(".")[:2])
			obreby_id.append(obreb_id)
		
		obreby_id = set(obreby_id)
		if len(obreby_id) ==1:
			obreb_id = next(iter(obreby_id))
			obreb_nazwa = df_GDDKIA[df_GDDKIA["obreb_id"] == obreb_id]["obreb"].values[0]
			obreb_gmina = df_GDDKIA[df_GDDKIA["obreb_id"] == obreb_id]["gmina"].values[0]
			obreb_powiat = df_GDDKIA[df_GDDKIA["obreb_id"] == obreb_id]["powiat"].values[0]
			self.kw_docelowa = df_GDDKIA[df_GDDKIA["obreb_id"] == obreb_id]["kw_gddkia"].values[0]

			return {'id':str(obreb_id), 'nazwa':obreb_nazwa, 'gmina':obreb_gmina,'powiat':obreb_powiat}

		print(f"UWAGA:dzialki we wniosku do: {self.kw} znajdują się w dwóch obrebach")
		return 


	def find_wlasciciele(self,df_relacje):
		"""Znajdz id wlascicieli kw na podstawie dzialek"""
		for dzialka in self.dzialki_zrodlowe:
			wlasciciele = df_relacje[df_relacje['ID_dzialki']==dzialka]['ID_wlasciciela'].tolist()
			self.wlasciciele += wlasciciele
		self.wlasciciele= list(set(self.wlasciciele))
		

	def pobierz_dane_wlascicieli(self,df_wlasiciele:pd.DataFrame):
		for id in self.wlasciciele:
			rekord = df_wlasiciele[df_wlasiciele["ID_osoby"]==id]
			if not rekord.empty:
				self.wlasciciele_dane.append(rekord.iloc[0].to_dict())

	
	def okresl_sad(self,sady):
		"""Przypisz sąd rejonowy na podstawie numeru kw"""
		prefix = self.kw.split("/")[0]
		self.sad = sady.get(prefix, "-")

	def okresl_zalaczniki(self):
		"""przygotuj dane do wpisania w Wykazie zalacznikow KW-WPIS/KW-ZAL"""
		self.zalaczniki = {}
		self.zalaczniki['kw_pp'] = 1

		if self.ile_wlascicieli > 2:
			self.zalaczniki['kw_wu'] = self.ile_wlascicieli - 2
	
		self.zalaczniki['inny1'] = self.odnosnik_do_zalacznika("DECYZJA WOJEWODY MAZOWIECKIEGO Z DNIA 06.12.2024R. ZNAK: 176/SPEC/2024")
		self.zalaczniki['inny2'] = self.odnosnik_do_zalacznika("PEŁNOMOCNICTWO")
	
	def odnosnik_do_zalacznika(self,zalacznik:str):
		"""jezeli wniosek nie jest pierwszym w obrebie, dodaj odsylacz do pierwszego wniosku"""
		if self.okresl_pierwszy_wniosek():
			return zalacznik
		else:
			suffix = f" - znajduje się w aktach {Wniosek.pierwszy_wniosek[self.obreb['id']]}"
			zalacznik += suffix
			return zalacznik
	
	def okresl_pierwszy_wniosek(self):
		"""sprawdza czy jest pierwszym wnioskiem dla obrebu, jezeli nie zwraca numer kw pierwszego wniosku"""
		pierwszy_wniosek = Wniosek.pierwszy_wniosek.get(self.obreb['id'])
		
		#jeżeli nie ma infromacji o pierwszym wniosku dla danego obrebu [przechowywanej w klasie] ustal 
		#aktualny wniosek jako pierwszy
		if not pierwszy_wniosek:
			Wniosek.pierwszy_wniosek[self.obreb['id']]=self.kw
			pierwszy_wniosek = self.kw
			
		if pierwszy_wniosek == self.kw:
			return True
		else:
			return False
	
	def get_output_path(self):
		path = ["export",f"Sąd rejonowy {self.sad}",self.obreb["nazwa"],self.kw.replace("/",".")]
		return os.path.join(*path) 
	
	def print_forms(self):
		for form in self.formularze:
			if form == "KW-WPIS":
				output_path=self.get_output_path()
				data={
					'sad':self.sad,
					'nr_kw':self.kw,
					'tresc_zadania':self.tresc_zadania,
				}

				print_wpis(data,self.wnioskodawca,self.wlasciciele_dane,self.zalaczniki, output_path)

	def okresl_tresc_zadania(self,dzialki_inwestycja_wszystkie:dict):
		#selekcja działek których dotyczy wniosek znajduje się w inwestycji
		dzialki_inwestycja = [dz for dz in self.dzialki if dz in dzialki_inwestycja_wszystkie]	
		#ile dzialek odlaczanych
		licznik_dzialek = len(dzialki_inwestycja)
	
		tresc = (
			f'WNOSZĘ O BEZOBCIĄŻENIOWE ODŁĄCZENIE NIERUCHOMOŚCI Z KSIĘGI WIECZYSTEJ {self.kw} ZGODNIE Z USTAWĄ Z DNIA 10 KWIETNIA'
			' 2003 R. "O SZCZEGÓLNYCH ZASADACH PRZYGOTOWANIA I REALIZACJI INWESTYCJI W ZAKRESIE DRÓG PUBLICZNYCH" '
			'(DZ.U. 2023 POZ. 162):')
		

		for num,dzialka in enumerate(dzialki_inwestycja):
			nowa_tresc = ""
			if dzialka in dzialki_inwestycja:
				nowa_tresc = f" DZIAŁKI NR {krotkie_id(dzialka)} O POW. {dzialki_inwestycja_wszystkie[dzialka]} HA,"
				tresc += nowa_tresc
			if num == licznik_dzialek -1 and num >0:
				nowa_tresc = f" ORAZ {nowa_tresc} "
				tresc = tresc[:-1] + nowa_tresc #tresc[:-1] usuwa ostatni przecinek przed "ORAZ"
		
		tresc += (
			f"POŁOŻONEJ W OBRĘBIE {krotkie_id(self.obreb["id"])} {self.obreb["nazwa"]}, GMINA {self.obreb["gmina"]}, "
			f"POWIAT {self.obreb["powiat"]} I PRZYŁĄCZENIE JEJ DO KSIĘGI {self.kw_docelowa}."
				)
		
		if licznik_dzialek > 1:
			tresc = tresc.replace("POŁOŻONEJ","POŁOŻONYCH")
			tresc = tresc.replace("JEJ", "ICH")		
		return tresc

if __name__ == "__main__":
	print(nazwisko_zlozone("głażejewicz-bąk"))