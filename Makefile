.PHONY: create-venv install test run docker-build docker-run clean

create-venv:
	python3.11 -m venv .venv
	source .venv/bin/activate
	pip install --upgrade pip

install:
	create-venv
	pip install -e .

test:
	pytest tests/ -v

run:
	uvicorn src.api.main:app --reload

docker-build:
	docker build -t postgresql-reviewer .

docker-run:
	docker-compose up --build

clean:
	rm -rf data/faiss/index.*
	rm -rf logs/*.log
	rm -rf __pycache__
	rm -rf src/**/*.pyc
	rm -rf .pytest_cache

health:
	curl http://localhost:8000/health

logs:
	tail -f logs/postgresql-reviewer.log
