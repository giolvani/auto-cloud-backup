from datetime import datetime
from logger import log_message
import backup_codebase
import backup_database


def run_backup():
    try:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        log_message("===> Início do backup. <===")

        try:
            backup_codebase.backup_codebases(timestamp)
        except Exception as e:
            log_message(f"Erro ao fazer backup dos repositórios: {e}")

        try:
            backup_database.backup_databases(timestamp)
        except Exception as e:
            log_message(f"Erro ao fazer backup dos bancos de dados: {e}")

        log_message("===> Backup finalizado. <===")
    except Exception as e:
        log_message(f"===> Erro geral ao executar backup: {e} <===")
        raise e


if __name__ == "__main__":
    run_backup()
