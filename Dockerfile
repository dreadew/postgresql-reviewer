FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ ./src/
COPY .env ./.env

RUN pip install --upgrade pip && pip install -e .

ENV TOKENIZERS_PARALLELISM=false

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
