from pypdf import PdfReader


class PDFRegistry:
    _stats: list[dict] = []

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
