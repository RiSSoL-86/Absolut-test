# Absolut-test Backend

Backend service built with Django and Django REST Framework.

See [docs/architecture.md](docs/architecture.md) for the data model,
indexes and performance characteristics.

## Local Setup

Create the local environment file from the example:

```bash
cp src/.env.example src/.env
```

Install dependencies and prepare git hooks:

```bash
make install
make pre-commit.install
```

Start local dependencies, apply migrations, create an admin user, and run the
development server:

```bash
make compose.deps.dev
make migrate
make createsuperuser
make run
```

The service will be available at:

- Swagger UI: http://localhost:8000/api/docs/
- Django admin: http://localhost:8000/admin/

## Local Checks

Run linters and type checks:

```bash
make lint
```

Run tests:

```bash
make test
```
