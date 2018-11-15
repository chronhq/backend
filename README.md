# Chron Backend

## Getting Started

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
