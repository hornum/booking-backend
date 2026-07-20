up:
	docker compose up -d

build-up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f app

revision:
	docker compose exec app alembic revision --autogenerate -m "$(m)"

upgrade:
	docker compose exec app alembic upgrade head

downgrade:
	docker compose exec app alembic downgrade -1
