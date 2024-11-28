import os
import tarfile
import subprocess
import json
import boto3
import shutil
from logger import log_message


def backup_repo(repo_url, repo_name, storage_config, temp_dir, timestamp):
    s3_client = boto3.client(
        "s3",
        endpoint_url=storage_config["endpoint_url"],
        aws_access_key_id=storage_config["access_key"],
        aws_secret_access_key=storage_config["secret_key"],
    )

    log_message(f"Starting backup of repository {repo_name}.")
    repo_path = os.path.join(temp_dir, repo_name)
    os.makedirs(temp_dir, exist_ok=True)

    try:
        subprocess.run(["git", "clone", repo_url, repo_path], check=True)

        tar_path = os.path.join(temp_dir, f"{repo_name}_backup.tar.gz")
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(repo_path, arcname=repo_name)

        storage_path = f"{timestamp}/codebase/{repo_name}_backup.tar.gz"
        log_message(f"Uploading to path: {storage_path}")

        s3_client.upload_file(Bucket=storage_config["bucket_name"], Key=storage_path, Filename=tar_path)
        log_message(f"Backup of repository {repo_name} completed.")

    except subprocess.CalledProcessError as e:
        log_message(f"Error during backup of repository {repo_name}: {e}")
    except Exception as e:
        log_message(f"General error in repository backup {repo_name}: {e}")
    finally:
        shutil.rmtree(repo_path, ignore_errors=True)


def backup_codebases(config_path, timestamp):
    with open(config_path) as config_file:
        config = json.load(config_file)

    if not config.get("codebase"):
        log_message("No repositories configured for backup.")
        return

    for group in config["codebase"]:
        repo_name = group["repo_name"]
        for repo_url in group["repositories"]:
            backup_repo(repo_url, repo_name, config["storage"], "./backups/codebase", timestamp)


if __name__ == "__main__":
    print("You shouldn't run this file directly.")
    pass
