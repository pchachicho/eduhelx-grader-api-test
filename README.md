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