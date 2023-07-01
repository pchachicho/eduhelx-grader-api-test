# EduHeLx Grader API
A microservice supporting student submissions to otter grader within EduHeLx


## Usage
### Installation
You'll need to have installed libpq (Postgres client) first before installing psycopg2 (Postgres driver).
python```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
## Running
python3```
uvicorn --reload app.main:app --log-level=info
```