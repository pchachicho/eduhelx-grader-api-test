# EduHeLx Grader API
A microservice supporting student submissions to otter grader within EduHeLx


## Usage

### Installation
You'll need to have installed libpq (Postgres client) first before installing psycopg2 (Postgres driver).
```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Setup .env
cp .env.sample .env
vim .env
```

### Running
```bash
set -a && source .env
python -m app.main
# or
uvicorn --reload app.main:app --log-level=info
```

## Application Startup

Our application startup is handled by the `start.py` script. This script performs
different actions depending on whether it's running inside a Kubernetes cluster
or in a Docker container.

When running in Kubernetes, we assume that a ConfigMap and a Secret are mounted
at `/etc/grader-config` and `/etc/grader-secret` respectively. These contain the
non-sensitive and sensitive configuration parameters for our application.
The `start.py` script will combine the values from these two sources into a
single `.env` file at `/app/.env`, which is then used by our application for its
configuration.

When running in Docker, we expect the `.env` file to be provided directly.
The `start.py` script checks for the existence of this file and if it doesn't
exist, it tries to load the environment variables using python-dotenv.

After the `.env` file has been created or checked, the `start.py` script starts
the application using the Uvicorn ASGI server.

## Password Secret Generator

The password secret generator is a Python script that generates a random
12-character alphanumeric password and creates a Kubernetes Secret with this
password. The name of the Secret is `grader-postgresql`.

Before creating the Secret, the script checks if a Secret with this name already
exists. If it does, the script prints a message and does not create a new Secret.
This prevents accidental overwriting of existing Secrets.

The generated password is used for the PostgreSQL database that our application
connects to. It's important to handle this password securely, as it provides
access to the database.
