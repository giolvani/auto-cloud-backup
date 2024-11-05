from datetime import datetime
import backup_codebase
import backup_database

LOG_FILE = "logs/backup.log"


def log_message(message):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{datetime.now()}: {message}\n")


def run_backup():
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    log_message("===> Início do backup. <===")

    # Executar backup do codebase
    backup_codebase.backup_codebases(timestamp)

    # Executar backup do banco de dados
    backup_database.backup_databases(timestamp)

    log_message("===> Backup finalizado. <===\n")


if __name__ == "__main__":
    run_backup()
