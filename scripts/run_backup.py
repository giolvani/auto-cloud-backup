import argparse
from datetime import datetime
from logger import log_message
import backup_codebase
import backup_database


def run_backup(config_path):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        log_message("===> Backup started. <===")

        try:
            backup_codebase.backup_codebases(config_path, timestamp)
        except Exception as e:
            log_message(f"Error backing up repositories: {e}")

        try:
            backup_database.backup_databases(config_path, timestamp)
        except Exception as e:
            log_message(f"Error backing up databases: {e}")

        log_message("===> Backup finished. <===")
    except Exception as e:
        log_message(f"===> General error executing backup: {e} <===")
        raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/settings.json", help="Path to the configuration file")
    args = parser.parse_args()
    run_backup(args.config)
