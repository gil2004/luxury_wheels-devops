# Luxury Wheels — DevOps Platform

A DevOps portfolio project. The application is a Flask car rental site; the project is everything around it — how it is packaged, tested, provisioned, configured, orchestrated, observed and updated.

The app is the payload, not the point.

## Why this app

It has real state: five tables, sessions, and availability logic that depends on dates. Stateless apps teach nothing about volumes, StatefulSets, backups or migrations.

## Current state

Phase 0 is complete. The application is ready to be operated by something else.

- Configuration read from the environment (`SECRET_KEY`, `DATABASE_PATH`) — no secrets in code
- `/health` (liveness) and `/ready` (readiness, checks the database)
- Served by Gunicorn instead of the Flask development server
- Passwords hashed with `werkzeug.security`
- Database schema and test fixtures versioned as SQL (`schema.sql`, `seed.sql`)
- Test suite with pytest: health, vehicle listing, booking conflicts, login
- Runtime and development dependencies split

Still SQLite. That changes in Phase 1.

## Stack

Python · Flask · Gunicorn · SQLite · pytest

Planned: Docker · PostgreSQL · GitHub Actions · Terraform · Ansible · Kubernetes (k3s) · Prometheus

## Layout

```
app/          the application (payload)
tests/        pytest suite
schema.sql    database schema
seed.sql      fixtures for tests
docs/         decisions and runbook
```

## Running locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env     # then set DATABASE_PATH to an absolute path
pytest -v

gunicorn --chdir app --bind 0.0.0.0:8000 main:app
```

The app is then available at `http://localhost:8000`.

## Roadmap

| Phase | Focus | Status |
|---|---|---|
| 0 | Application preparation | done |
| 1 | Docker, SQLite → PostgreSQL | next |
| 2 | CI: lint, test, build, scan, push | |
| 3 | Terraform: server and ephemeral staging, plus CD | |
| 4 | Ansible: roles, k3s | |
| 5 | Kubernetes: deployment, ingress, state | |
| 6 | Prometheus, Grafana, business metrics | |
| 7 | Backups, chaos testing, runbook | |
