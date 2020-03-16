# import config
# You can change the default config with `make cnf="config_special.env" [command]`
cnf ?= django.env
include $(cnf)

# Documentation
.PHONY: help

help: ## Displays this message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

# Git revision

REV := $(shell git rev-parse --short HEAD)

# Docker tasks

CONTAINERS := $(shell docker ps -q)

build: ## Builds and tags containers
	docker-compose build

run: ## Builds, starts, and runs containers
	docker-compose up --build -d

run_prod: ## Builds, starts, and runs containers with production config
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

stop: ## Stops running containers
	docker-compose stop

clean: ## Stop and remove containers, networks, volmes, and images
	docker-compose down

# Debug tools
run_debug: ## Builds, starts, and runs containers, running the built-in Django web server
	docker-compose run --entrypoint sh --service-ports web init.sh python manage.py runserver 0.0.0.0:81

exec_debug: ## Runs built-in Django web server
	docker-compose exec web python manage.py runserver 0.0.0.0:81

# Documentation
graph: ## Builds a UML class diagram of the models
	docker-compose exec web python manage.py graph_models -a -g -o graph.svg

# Misc
test: ## Builds, starts, and runs containers, running the django tests
	docker-compose run --entrypoint sh --service-ports web init.sh python manage.py test --debug-mode

exec_test: ## Executes django tests in a running container
	docker-compose exec web python manage.py test --debug-mode

exec_testk: ## Executes django tests in a running container, keeping the database schema from the previous test run
	docker-compose exec web python manage.py test -k --debug-mode

lint: ## Lints python files to pass CI
	docker-compose exec web black . --exclude /migrations/
	docker-compose exec web pylint --ignore=tests ./api/
	docker-compose exec web pylint --rcfile=api/tests/pylintrc ./api/tests

bash: ## Create shell in web container
	docker-compose exec web sh

shell: ## Open the django shell (https://django-extensions.readthedocs.io/en/latest/shell_plus.html)
	docker-compose exec web python manage.py shell_plus

dbshell: ## Create psql shell
	docker-compose exec -u postgres db psql

admin: ## Creates a super user based on the values supplied in the configuration file (must be running)
	docker-compose exec web ./manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('$(ADMIN_USER)', '$(ADMIN_EMAIL)', '$(ADMIN_PASS)')"

# Geometry
mvt-build: ## Generates mbtiles for STVs
	docker-compose exec mbtiles sh /scripts/getSTVGeoJSON.sh 
	docker-compose exec mbtiles /bin/rm -f /root/mbtiles/stv.mbtiles
	docker-compose restart mbtiles
	docker-compose exec mbtiles /bin/mv /tmp/stv.mbtiles /root/mbtiles/stv.mbtiles

mvt-update: ## Update mbtiles for STVs
	docker-compose exec -T mbtiles sh /scripts/pullUpdatedSTVs.sh 
	docker-compose exec -T mbtiles sh -c "[ -f /tmp/stv.mbtiles ] && /bin/rm -f /root/mbtiles/stv.mbtiles || echo No changes"
	[ -f ./data/mbtiles/stv.mbtiles ] && echo "No need for restart" || docker-compose restart mbtiles
	docker-compose exec -T mbtiles sh -c "[ -f /tmp/stv.mbtiles ] && /bin/mv /tmp/stv.mbtiles /root/mbtiles/stv.mbtiles || echo skipping"

# Docker images
image: ## Build backend:latest image
	docker build -t chronmaps/backend:latest .

push-image: ## Push backend:latest image
	docker push chronmaps/backend:latest

python-image: ## Build image with python dependencies
	docker build -t chronmaps/backend:deps-python -f Dockerfile.python .

push-python: ## Push python image
	docker push chronmaps/backend:deps-python

check-python-image:
	docker run --entrypoint md5sum chronmaps/backend:deps-python /requirements.txt| sed 's%/%config/%' | md5sum --check -

system-image: ## Build alpine with dependencies
	docker build -t chronmaps/backend:deps-base -f Dockerfile.base .
	docker build -t chronmaps/backend:deps-build -f Dockerfile.build .

push-system: ## Push alpine with dependencies
	docker push chronmaps/backend:deps-base
	docker push chronmaps/backend:deps-build

pull-images: ## Pull all images from docker.hub
	docker pull --all-tags chronmaps/backend

dumpdata: ## Dump data from the database
	docker-compose exec web python manage.py dumpdata -e contenttypes -e auth.Permission -e sessions --indent=2 | \
	xz -z -T 0 > project/$$(date +%Y-%m-%d).dump.json.xz

loaddata: ## Restore data from previous dump
	NAME=$$(ls project |grep "^20[0-9][0-9]-[0-9]" | sort -r | head -n 1| sed -e 's%.json%%' -e 's%.xz%%'); \
	if [ -z "$${NAME}" ]; then \
		echo "Dumped data not detected"; \
		exit 1; \
	fi; \
	echo "Selected filename $${NAME}"; \
	if [ -f "project/$${NAME}.json.xz" ]; then \
		echo "Extracting file"; \
		xz -d project/$${NAME}.json.xz; \
	fi; \
	if [ -f "project/$${NAME}.json" ]; then \
		echo Loading $${NAME}.json; \
		docker-compose exec web python manage.py loaddata $${NAME}.json; \
	else \
		echo Error: No file to load; \
	fi;

dumpsql: ## dump all data using pg_dumpall
	docker-compose exec -T db sh -c 'echo localhost:5432:$$POSTGRES_DB:$$POSTGRES_USER:$$POSTGRES_PASSWORD > ~/.pgpass; chmod 600 ~/.pgpass'
	docker-compose exec -T db sh -c 'pg_dumpall -U $$POSTGRES_USER -f /docker-entrypoint-initdb.d/$$(date "+%Y-%m-%d").dump'