FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=2.2.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-root --only main

COPY src/ /app/

ENV PORT=8000 \
    WEB_CONCURRENCY=1

EXPOSE ${PORT}

CMD ["gunicorn", "django_project.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "30", \
     "--max-requests", "65536", \
     "--max-requests-jitter", "200", \
     "--access-logfile", "-", \
     "--capture-output"]
