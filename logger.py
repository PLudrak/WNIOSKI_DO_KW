import logging
from logging.handlers import RotatingFileHandler
import os

# Utwórz folder na logi (jeśli nie istnieje)
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Ścieżka do pliku logów
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Konfiguracja loggera
logger = logging.getLogger("my_app_logger")
logger.setLevel(logging.DEBUG)  # loguj wszystko od DEBUG w górę

# Format wiadomości logów
formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")

# Handler do pliku z rotacją (np. 1 MB na plik, max 3 pliki)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)  # do pliku tylko INFO+

# Handler do konsoli (np. dla devów)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.WARNING)

# Dodaj handlery do loggera
logger.addHandler(file_handler)
logger.addHandler(console_handler)
