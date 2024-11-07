import os
import subprocess
import tarfile
import json
import boto3
import shutil
from datetime import datetime
from logger import log_message  # Importar a função log_message

with open("config/settings.json") as config_file:
    config = json.load(config_file)

TEMP_DIR = "./backups/database"
BUCKET_NAME = config["storage"]["bucket_name"]
ENDPOINT_URL = config["storage"]["endpoint_url"]
ACCESS_KEY = config["storage"]["access_key"]
SECRET_KEY = config["storage"]["secret_key"]


s3_client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)


def create_cnf_file(db_config):
    cnf_content = f"[client]\nuser = {db_config['user']}\npassword = {db_config['password']}\nhost = {db_config['host']}\nport = {db_config['port']}"

    cnf_path = f"config/{db_config['name']}_config.cnf"
    with open(cnf_path, "w") as cnf_file:
        cnf_file.write(cnf_content)

    return cnf_path


def backup_database(db_config, timestamp):
    db_name = db_config["name"]
    db_user = db_config["user"]
    db_password = db_config["password"]
    db_host = db_config["host"]
    db_port = str(db_config["port"])
    db_type = db_config.get("type", "postgres")

    log_message(f"Iniciando backup do banco de dados {db_type} {db_name}...")

    os.makedirs(TEMP_DIR, exist_ok=True)
    dump_path = os.path.join(TEMP_DIR, f"{db_name}_backup.sql")

    if db_type == "postgres":
        cnf_path = None
        dump_command = [f"PGPASSWORD={db_password}"]
        dump_command.extend(
            ["pg_dump", "-h", db_host, "-p", db_port, "-U", db_user, db_name]
        )
    elif db_type == "mysql":
        cnf_path = create_cnf_file(db_config)
        dump_command = ["mysqldump", f"--defaults-extra-file={cnf_path}", db_name]
    else:
        log_message(f"Tipo de banco de dados não suportado: {db_type}")
        return

    try:
        if "ssh" in db_config:
            ssh_info = db_config["ssh"]
            ssh_command = [
                "ssh",
                "-i",
                ssh_info["identity_file"],
                "-p",
                str(ssh_info["port"]),
                f"{ssh_info['user']}@{ssh_info['host']}",
            ]
            dump_command = ssh_command + dump_command
            shell = False
        else:
            shell = False

        with open(dump_path, "w") as dump_file:
            subprocess.run(dump_command, stdout=dump_file, check=True, shell=shell)

        tar_path = os.path.join(TEMP_DIR, f"{db_name}_backup.tar.gz")
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(dump_path, arcname=os.path.basename(dump_path))

        storage_path = f"{timestamp}/database/{db_name}_backup.tar.gz"
        log_message(f"Uploading to path: {storage_path}")

        s3_client.upload_file(Bucket=BUCKET_NAME, Key=storage_path, Filename=tar_path)
        log_message(f"Backup do banco de dados {db_name} concluído.")

        shutil.rmtree(TEMP_DIR)

        if cnf_path:
            os.remove(cnf_path)

    except subprocess.CalledProcessError as e:
        log_message(f"Erro ao executar o dump do banco de dados {db_name}: {e}")
    except Exception as e:
        log_message(f"Erro geral no backup do banco de dados {db_name}: {e}")


def backup_databases(timestamp):
    if not config["databases"]:
        log_message("Nenhum banco de dados configurado para backup.")
        return

    for db in config["databases"]:
        backup_database(db, timestamp)


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    backup_databases(timestamp)
