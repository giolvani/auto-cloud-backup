# AutoCloudBackup

**AutoCloudBackup** is an open-source solution for automated database and code repository backups, with support for cloud storage providers such as DigitalOcean Spaces and AWS S3. It’s ideal for anyone looking for a simple, reliable, and customizable way to secure their data.

## Features

- **Supports MySQL and PostgreSQL**: Perform automated backups for databases with secure credential management.
- **Code Repository Backup**: Includes support for Git repository backups.
- **Cloud Storage**: Upload backups directly to DigitalOcean Spaces and AWS S3.
- **Easy Configuration**: Configure databases, repositories, and storage in `settings.json`.

## Prerequisites

- Python 3.x
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/AutoCloudBackup.git
cd AutoCloudBackup
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS and Linux
# .\venv\Scripts\activate  # On Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure `settings.json` with your database, repository, and storage details.


## Usage

### Backup

To start the database backup, run the following command:

```bash
python scripts/run_backup.py
```

### Scheduling with cron

To schedule daily backups, add a cron entry:

```bash
0 2 * * * cd /path/to/AutoCloudBackup && python scripts/run_backup.py
```

### Configuring settings.json

The configuration file `settings.json` is used to define the databases, repositories, and storage details. Below is a sample configuration:

```json
{
    "databases": [
        {
            "name": "your_database",
            "user": "your_db_user",
            "password": "your_password",
            "host": "your_db_host",
            "port": "your_db_port",
            "type": "mysql",  // Use "postgres" for PostgreSQL
            "ssh": {
                "host": "optional_ssh_host",
                "user": "optional_ssh_user",
                "port": "optional_ssh_port",
                "identity_file": "path/to/your/ssh_key.pem"
            }
        }
    ],
    "repos": [
        {
            "profile": "GitProfileName",
            "repositories": [
                "git@github.com:YourUsername/YourRepo1.git",
                "git@github.com:YourUsername/YourRepo2.git"
            ]
        }
    ],
    "storage": {
        "type": "remote", // Use "local" for local storage. If "local", you don't need to set the next fields.
        "bucket_name": "your_bucket_name",
        "region": "nyc3",
        "endpoint_url": "https://nyc3.digitaloceanspaces.com",
        "access_key": "your_access_key",
        "secret_key": "your_secret_key"
    }
}
```

- databases: List your databases with their access credentials.
- repos: List the Git repositories you wish to back up.
- storage: Configure your cloud storage provider for backups, or local storage if desired.

### Storage Configuration

The application supports both local and remote storage configurations for backups. If the `storage.type` in your configuration is set to `"local"`, the backup files will be saved locally and will not be deleted after the backup process. This allows you to retain local copies of your database dumps for additional security or manual access.

## Security Considerations

To avoid exposing your credentials:
- Use `.pgpass` for PostgreSQL or `.my.cnf` for MySQL to store your credentials when possible.
- Ensure file permissions are properly set for any sensitive files.
