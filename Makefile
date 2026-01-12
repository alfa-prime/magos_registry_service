COMPOSE_DEV = docker compose -f docker-compose.dev.yml
COMPOSE_PROD = docker compose -f docker-compose.prod.yml

.PHONY: up-dev down-dev logs-dev up-prod down-prod check format

# РАЗРАБОТКА
up-dev:
	$(COMPOSE_DEV) up --build -d

down-dev:
	$(COMPOSE_DEV) down

logs-dev:
	$(COMPOSE_DEV) logs -f app

bash-dev:
	$(COMPOSE_DEV) exec app bash


# ПРОДАКШЕН
up-prod:
	$(COMPOSE_PROD) up --build -d

down-prod:
	$(COMPOSE_PROD) down

logs-prod:
	$(COMPOSE_PROD) logs -f app

bash-prod:
	$(COMPOSE_PROD) exec app bash

clean:
	docker system prune -a --volumes -f


# КАЧЕСТВО КОДА
check:
	ruff check .

format:
	ruff format .

# Сборка проекта для LLM
to-llm:
	files-to-prompt . -m > to_llm.md