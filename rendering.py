from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

def load_template(template_name: str):
    env = Environment(loader=FileSystemLoader(['forms', 'static']))
    return env.get_template(template_name)

def rozdziel_uczestnikow(wlasciciele: list[dict]):
    uczestnik1 = wlasciciele[0] if len(wlasciciele) > 0 else {}
    uczestnik2 = wlasciciele[1] if len(wlasciciele) > 1 else {}
    pozostali = wlasciciele[2:] if len(wlasciciele) > 2 else []
    return uczestnik1, uczestnik2, pozostali

def print_wpis(data, wnioskodawca, wlasciciele,zalaczniki,path):
	base_path = os.path.abspath("forms")
	output_path = os.path.join(path,"KW-WPIS.pdf")
	os.makedirs(os.path.dirname(output_path), exist_ok=True)

	u1,u2,pozostali_uczestnicy = rozdziel_uczestnikow(wlasciciele)
	
	strony = [
		("KW-WPIS_1.html", {"numer_strony":"1"}),
		("KW-WPIS_2.html", {"numer_strony":"2"}),
		("KW-WPIS_3.html", {"numer_strony":"3", "uczestnik":u1, "wnioskodawca":wnioskodawca}),
		("KW-WPIS_4.html", {"numer_strony":"4", "uczestnik":u2, "zalaczniki":zalaczniki})
	]
	rendered_pages = []

	for template_name, context in strony:
		template = load_template(template_name)
		html = template.render(**data,**context)
		rendered_pages.append(html)

	combined_html = "".join(rendered_pages)
	while True:
		try:
			HTML(string=combined_html, base_url=base_path).write_pdf(output_path)
			print(f"Zapisano wniosek {output_path}")
			break
		except:
			print("Błąd zapisu \n sprobowac ponownie? T/N")
			odp = input().strip().lower()
			if odp != 't':
				print("zapis przerwany")
				break