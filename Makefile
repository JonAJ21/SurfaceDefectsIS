DC = docker-compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env

DOCKER_COMPOSE_FILE = docker-compose.yaml
AUTH_CONTAINER = auth-service

.PHONY: app
app:
	${DC} -f ${DOCKER_COMPOSE_FILE} ${ENV} up --build -d

.PHONY: app-up
app-up:
	${DC} -f ${DOCKER_COMPOSE_FILE} ${ENV} up -d

.PHONY: app-down
app-down:
	${DC} -f ${DOCKER_COMPOSE_FILE} down

.PHONY: auth-shell
auth-shell:
	${EXEC} ${AUTH_CONTAINER} bash

.PHONY: auth-logs
auth-logs:
	${LOGS} ${AUTH_CONTAINER} -f

.PHONY: auth-alembic-revision
auth-alembic-revision:
	${EXEC} ${AUTH_CONTAINER} alembic -c ./infrastructure/alembic.ini revision --autogenerate -m "update"

.PHONY: auth-alembic-upgrade
auth-alembic-upgrade:
	${EXEC} ${AUTH_CONTAINER} alembic -c ./infrastructure/alembic.ini upgrade head

.PHONY: auth-init
auth-init:
	${EXEC} ${AUTH_CONTAINER} python cli.py