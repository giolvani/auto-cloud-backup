import os
import tarfile
import subprocess
import json
import boto3
import shutil
from datetime import datetime

with open("config/settings.json") as config_file:
    config = json.load(config_file)

TEMP_DIR = "./backups/codebase"
LOG_FILE = "logs/backup.log"
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


def log_message(message):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{datetime.now()}: {message}\n")


def backup_repo(repo_url, profile_name, timestamp):
    repo_name = os.path.basename(repo_url).replace(".git", "")
    log_message(f"Iniciando backup do repositório {repo_name}.")

    repo_path = os.path.join(TEMP_DIR, repo_name)
    os.makedirs(TEMP_DIR, exist_ok=True)
    subprocess.run(["git", "clone", "--mirror", repo_url, repo_path], check=True)

    tar_path = f"{TEMP_DIR}/{repo_name}_backup.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(repo_path, arcname=repo_name)

    storage_path = f"{timestamp}/codebase/{profile_name}/{repo_name}_backup.tar.gz"
    log_message(f"Uploading to path: {storage_path}")

    s3_client.upload_file(Bucket=BUCKET_NAME, Key=storage_path, Filename=tar_path)
    log_message(
        f"Backup do repositório {repo_name} do perfil {profile_name} concluído."
    )

    shutil.rmtree(TEMP_DIR)


def backup_codebases(timestamp):
    for profile in config["repos"]:
        log_message(
            f"Iniciando backup dos repositórios do perfil: {profile['profile']}"
        )
        for repo_url in profile["repositories"]:
            backup_repo(repo_url, profile["profile"], timestamp)


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    backup_codebases(timestamp)
