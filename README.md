# Chron Backend

## Getting Started

### Docker

```bash
# Clone the repo
git clone https://github.com/chronoscio/backend
cd backend

# Create env files, remember to update accordingly
cp django.env.sample django.env
cp postgres.env.sample postgres.env

# Build and start the docker containers
make run

# Navigate to http://localhost/
# 502 error means postgres is starting, try again in a few seconds
```

### Local

```bash
# Clone the repo
git clone https://github.com/chronoscio/backend
cd backend

# Create and activate virtual environment
virtualenv venv
source venv/bin/activate # *nix
venv/Scripts/activate # win
pip install -r config/requirements.txt

python project/manage.py runserver
```
