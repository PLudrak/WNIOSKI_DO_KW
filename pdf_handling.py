import os
from pypdf import PdfReader, PdfWriter, PdfMerger


class PDFRegistry:
    _stats: list[dict] = []
    _dirs = []

    @classmethod
    def add(cls, path):
        stat = {"path": path, "pages": cls.pages_counter(path)}
        cls._stats.append(stat)

    @classmethod
    def get_all(cls):
        return cls._stats.copy()

    @classmethod
    def clear(cls):
        cls._stats.clear()

    @classmethod
    def pages_counter(cls, path):
        reader = PdfReader(path)
        return len(reader.pages)

    @classmethod
    def get_dirs(cls):

        dirs_list = []

        for item in cls._stats:
            dirs_list.append(item["path"])

        return set(dirs_list)


def dodaj_puste_strony():
    """dodaje pustą stronę na końcu wniosku lub załącznika jeżeli liczba stron jest nieparzysta"""
    print("merging")
    lista_pdf = PDFRegistry.get_all()

    for item in lista_pdf:
        path = item["path"]
        num_pages = item["pages"]

        if num_pages % 2 == 1:
            reader = PdfReader(path)
            writer = PdfWriter()

            # dodawanie istniejących stron do writera
            for page in reader.pages:
                writer.add_page(page)

            # dodawanie strony A4
            writer.add_blank_page(
                width=595.276, height=841.890
            )  # A4 w punktach (72dpi)

            with open(path, "wb") as f:
                writer.write(f)


def merge_wniosek():
    """Połącz poszczególne strony i załączniki we wnioski na podstawie ścieżek z PDFRegistry"""
    dodaj_puste_strony()
    grouped_files = {}

    for item in PDFRegistry.get_all():
        path = item["path"]
        folder = os.path.dirname(path)
        grouped_files.setdefault(folder, []).append(path)

    for folder, files in grouped_files.items():
        writer = PdfWriter()
        for path in files:
            writer.append(path)

        output_file = os.path.join(folder, "Wniosek.pdf")
        with open(output_file, "wb") as f:
            writer.write(f)
        writer.close()


def merge_wnioski_obreb(base_dir="export"):
    for sad in os.listdir(base_dir):
        sad_path = os.path.join(base_dir, sad)
        if not os.path.isdir(sad_path):
            continue

        for obreb in os.listdir(sad_path):
            obreb_path = os.path.join(sad_path, obreb)
            if not os.path.isdir(obreb_path):
                continue

            writer = PdfWriter()
            for nr_kw in os.listdir(obreb_path):
                nr_kw_path = os.path.join(obreb_path, nr_kw)
                wniosek_path = os.path.join(nr_kw_path, "Wniosek.pdf")

                if os.path.isfile(wniosek_path):
                    reader = PdfReader(wniosek_path)
                    for page in reader.pages:
                        writer.add_page(page)

            output_pdf_path = os.path.join(sad_path, f"{obreb}_wnioski.pdf")
            if writer.pages:
                with open(output_pdf_path, "wb") as f:
                    writer.write(f)
                print(f"Zapisano: {output_pdf_path}")
            else:
                print(f"Brak wniosków do połączenia w: {obreb_path}")
