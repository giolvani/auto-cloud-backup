import os
import subprocess
import tarfile
import json
import boto3
import shutil
from logger import log_message

def create_cnf_file(db_config):
    cnf_content = f"[client]\nuser = {db_config['user']}\npassword = {db_config['password']}\nhost = {db_config['host']}\nport = {db_config['port']}"

    cnf_path = f"config/{db_config['name']}_config.cnf"
    with open(cnf_path, "w") as cnf_file:
        cnf_file.write(cnf_content)

    return cnf_path


def backup_database(db_config, storage_config, temp_dir, timestamp):
    db_name = db_config["name"]
    db_user = db_config["user"]
    db_password = db_config["password"]
    db_host = db_config["host"]
    db_port = str(db_config["port"])
    db_type = db_config.get("type", "postgres")

    s3_client = boto3.client(
        "s3",
        endpoint_url=storage_config["endpoint_url"],
        aws_access_key_id=storage_config["access_key"],
        aws_secret_access_key=storage_config["secret_key"],
    )

    log_message(f"Initiating backup of {db_type} database {db_name}...")

    os.makedirs(temp_dir, exist_ok=True)
    dump_path = os.path.join(temp_dir, f"{db_name}_backup.sql")

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
        log_message(f"Unsupported database type: {db_type}")
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

        tar_path = os.path.join(temp_dir, f"{db_name}_backup.tar.gz")
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(dump_path, arcname=os.path.basename(dump_path))

        storage_path = f"{timestamp}/database/{db_name}_backup.tar.gz"
        log_message(f"Uploading to path: {storage_path}")

        s3_client.upload_file(Bucket=storage_config["bucket_name"], Key=storage_path, Filename=tar_path)
        log_message(f"Backup of database {db_name} completed.")

    except subprocess.CalledProcessError as e:
        log_message(f"Error executing database dump of {db_name}: {e}")
    except Exception as e:
        log_message(f"General error in database backup of {db_name}: {e}")
    finally:
        shutil.rmtree(temp_dir)
        if cnf_path:
            os.remove(cnf_path)


def backup_databases(config_path, timestamp):
    with open(config_path) as config_file:
        config = json.load(config_file)

    if not config["databases"]:
        log_message("No databases configured for backup.")
        return

    for db in config["databases"]:
        backup_database(db, config["storage"], "./backups/database", timestamp)


if __name__ == "__main__":
    print("You shouldn't run this file directly.")
    pass
