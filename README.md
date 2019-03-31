# Chron Backend

[![Build Status](https://travis-ci.org/chronhq/backend.svg?branch=master)](https://travis-ci.org/chronhq/backend)
[![Requirements Status](https://requires.io/github/chronhq/backend/requirements.svg?branch=master)](https://requires.io/github/chronhq/backend/requirements/?branch=master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5fa15e25779540978040d406d69929b3)](https://www.codacy.com/app/chronhq/backend?utm_source=github.com&utm_medium=referral&utm_content=chronhq/backend&utm_campaign=Badge_Grade)

## Getting Started

### Docker

```bash
# Clone the repo
git clone https://github.com/chronoscio/backend
cd backend

# Create env files, remember to update accordingly
cp django.env.sample django.env
cp postgres.env.sample postgres.env
cp mbtiles.env.sample mbtiles.env

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

cd project
python manage.py runserver # must be executed from the project directory
```

## Production

First, run `cp config/nginx/allowed_ips.conf.sample config/nginx/allowed_ips.conf` and edit the new file to whitelist IPs that should have write access to the API. This is required for the time being to run the API in production. After this, `make run_prod` can then be used to configure the containers for a production setup. 
