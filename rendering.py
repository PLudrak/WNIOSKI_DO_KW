from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
def load_template(template):
	env = Environment(loader=FileSystemLoader(['forms','static']))
	template = env.get_template(template)
	return template


def print_wpis(data, wnioskodawca, wlasciciele):
	base_path = os.path.abspath("forms")
	template = load_template(r"KW-WPIS_1.html")
	html = template.render(**data,numer_strony="1")
	HTML(string=html, base_url=base_path).write_pdf("1.pdf")
	
	template = load_template(r"KW-WPIS_2.html")
	html = template.render(**data,numer_strony="2")
	HTML(string=html, base_url=base_path).write_pdf("2.pdf")

	template = load_template(r"KW-WPIS_3.html")
	html = template.render(**data,wnioskodawca=wnioskodawca,uczestnik=wlasciciele[0],numer_strony="3")
	HTML(string=html, base_url=base_path).write_pdf("3.pdf")

	template = load_template(r"KW-WPIS_4.html")
	html = template.render(**data,numer_strony="4")
	HTML(string=html, base_url=base_path).write_pdf("4.pdf")