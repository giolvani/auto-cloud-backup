import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

LOG_FILE = "logs/backup.log"

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

ENV = os.getenv("ENV", "development")


def log_message(message):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{datetime.now()}: {message}\n")

    if ENV == "development":
        print(message)
