# import config
# You can change the default config with `make cnf="config_special.env" [command]`
cnf ?= django.env
include $(cnf)

# Documentation
.PHONY: help

help: ## Displays this message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

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

rm: ## Stops and removes all running containers
	docker kill $(CONTAINERS)
	docker rm $(CONTAINERS)

clean: ## Stop and remove containers, networks, volmes, and images
	docker-compose down

# Debug tools
run_debug: ## Builds, starts, and runs containers, running the built-in Django web server
	docker-compose run --service-ports web sh init.sh python manage.py runserver 0.0.0.0:81

exec_debug: ## Runs built-in Django web server
	docker-compose exec web python manage.py runserver 0.0.0.0:81

# Documentation
graph: ## Builds a UML class diagram of the models
	docker-compose exec web python manage.py graph_models -a -g -o graph.svg

# Misc
test: ## Builds, starts, and runs containers, running the django tests
	docker-compose run --service-ports web sh init.sh python manage.py test --debug-mode

exec_test: ## Executes django tests in a running container
	docker-compose exec web python manage.py test --debug-mode

exec_testk: ## Executes django tests in a running container, keeping the database schema from the previous test run
	docker-compose exec web python manage.py test -k --debug-mode

lint: ## Lints python files to pass CI
	docker-compose exec web black . --exclude /migrations/
	docker-compose exec web pylint ./api/

bash: ## Create shell in web container
	docker-compose exec web sh

shell: ## Open the django shell (https://django-extensions.readthedocs.io/en/latest/shell_plus.html)
	docker-compose exec web python manage.py shell_plus

dbshell: ## Create psql shell
	docker-compose exec -u postgres db psql

admin: ## Creates a super user based on the values supplied in the configuration file (must be running)
	docker-compose exec web ./manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('$(ADMIN_USER)', '$(ADMIN_EMAIL)', '$(ADMIN_PASS)')"

# Geometry
mvt-ap: ## Generates mbtiles for APs
	docker-compose exec db bash /docker-entrypoint-initdb.d/scripts/getAPGeoJSON.sh
	docker-compose exec mbtiles bash /scripts/buildMVT.sh ap
	docker-compose exec mbtiles /bin/rm -f /root/mbtiles/ap.mbtiles
	docker-compose restart mbtiles
	docker-compose exec mbtiles /bin/mv /tmp/ap.mbtiles /root/mbtiles/ap.mbtiles

mvt-stv: ## Generates mbtiles for STVs
	docker-compose exec db bash /docker-entrypoint-initdb.d/scripts/getSTVGeoJSON.sh
	docker-compose exec mbtiles bash /scripts/buildMVT.sh stv
	docker-compose exec mbtiles /bin/rm -f /root/mbtiles/stv.mbtiles
	docker-compose restart mbtiles
	docker-compose exec mbtiles /bin/mv /tmp/stv.mbtiles /root/mbtiles/stv.mbtiles
