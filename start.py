import os
import glob
import subprocess
import sys
from dotenv import load_dotenv
from alembic.config import Config
from alembic import command


def main():
    # Mapping table for special case filename transformations
    special_cases = {
        "postgres-password": "POSTGRES_PASSWORD"
    }

    # Paths where ConfigMap and Secret are mounted
    config_path = "/etc/grader-config"
    secret_path = "/etc/grader-secret"

    # Path where .env file will be created
    env_path = "/app/.env"

    # Check if running in Kubernetes
    if os.path.isdir(config_path) or os.path.isdir(secret_path):
        # Get list of all files in ConfigMap and Secret
        config_files = glob.glob(os.path.join(config_path, "*"))
        secret_files = glob.glob(os.path.join(secret_path, "*"))

        # Combine ConfigMap and Secret into a single .env file
        with open(env_path, "w") as env_file:
            for filepath in config_files + secret_files:
                filename = os.path.basename(filepath)
                key = special_cases.get(filename, filename)
                with open(filepath, "r") as file:
                    env_file.write(f"{key}={file.read().strip()}\n")

    # If .env file exists, turn it into env variables
    if os.path.exists(env_path):
        load_dotenv(env_path)

    # Run Alembic migrations
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    # Start the application
    subprocess.run(["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])


if __name__ == "__main__":
    main()
