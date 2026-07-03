# Absolut-test — Backend

Синхронный API-сервис на **Django + Django REST Framework**. Конфигурация —
через `.env`. Автодокументация — **drf-spectacular** (Swagger UI / ReDoc).

Это синхронный DRF-близнец асинхронного шаблона `Django-DMR-Template`:
одинаковая структура и инфраструктура (celery, redis, sentry, email,
whitenoise), отличие — движок API (DRF вместо DMR) и `.env` вместо `config.toml`.

## Структура

- `src/apps/` — ядро: модели и сервисные функции сущностей (`apps/users`).
- `src/django_project/` — настройки проекта (`settings/*`, `urls.py`, `wsgi/asgi`, celery).
- `src/services/api/` — API-слой DRF: `views.py`, `serializers.py`, `urls.py`.

## Эндпоинты

| URL | Назначение |
|-----|------------|
| `/api/users/me/` | Текущий пользователь (аутентификация пока отключена — все эндпоинты открыты) |
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | OpenAPI-схема (yaml) |
| `/admin/` | Django-админка |

## Конфигурация

Все настройки читаются из `src/.env` (см. `src/.env.example`). Файл читают и
Django (`settings/__init__.py`, мини-загрузчик без зависимостей), и Docker
Compose (`env_file: ./src/.env`).

```bash
cp src/.env.example src/.env
```

## Локальная разработка (Django локально + БД в Docker)

```bash
make install            # poetry install
make compose.deps.dev   # поднять postgres + redis (network_mode: host)
make migrate
make createsuperuser
make run                # http://localhost:8000
```

Затем: Swagger — http://localhost:8000/api/docs/, `/me` —
http://localhost:8000/api/users/me/, админка — http://localhost:8000/admin/.

## Полный стек в Docker

```bash
make up      # deps + backend + celery (всё через network_mode: host)
make down
make logs
```

> **Docker за прокси / без IPv6.** Если `make up` не может собрать образ из-за
> недоступности PyPI (`Network is unreachable` / IPv6 timeout), пропишите в
> Docker Desktop → Settings → Docker Engine публичный DNS и перезапустите Docker:
> ```json
> { "dns": ["1.1.1.1", "8.8.8.8"] }
> ```
> Dockerfile уже отдаёт приоритет IPv4 (`/etc/gai.conf`), чтобы не упираться в
> заблокированный IPv6-egress.

## Команды

```bash
make lint    # ruff format + ruff check --fix + mypy
make test    # pytest (нужны поднятые postgres/redis из compose.deps.dev)
make celery  # celery-воркер локально
```
