import logging
from logging.handlers import RotatingFileHandler
import os
import time

# Utwórz folder na logi (jeśli nie istnieje)
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Unikalna nazwa pliku logu z datą i godziną
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = os.path.join(LOG_DIR, f"app_{timestamp}.log")

# dodanie poziomu "SAVED"
SAVE_LEVEL = 21
logging.addLevelName(SAVE_LEVEL, "SAVE")


def save(self, message, *args, **kwargs):
    if self.isEnabledFor(SAVE_LEVEL):
        self._log(SAVE_LEVEL, message, args, **kwargs)


logging.Logger.save = save  # type: ignore


# Konfiguracja loggera
logger = logging.getLogger("my_app_logger")
logger.setLevel(logging.DEBUG)  # loguj wszystko od DEBUG w górę

# Format wiadomości logów
formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")

# Handler do pliku z rotacją (np. 1 MB na plik, max 3 pliki)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

# Handler do konsoli (np. dla devów)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.ERROR)

# Dodaj handlery do loggera
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("   #### ROZPOCZĘTO DZIAŁANIE PROGRAMU ####")


def shorten_front(text: str, length=40):
    """Ucina początek tekstu"""
    if len(text) > length:
        text = "..." + text[-length:].strip()
    return text


def shorten_back(text: str, length=40):
    """Ucina koniec tekstu"""
    if len(text) > length:
        text = text[:length].strip() + "..."
    return text
