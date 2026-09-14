# Clinic Hub

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python env/dependency manager)
- Node.js 22+
- npm
- PostgreSQL
- Redis
- Docker + Docker Compose (only if running with containers)

## Local Run (non-Docker)

1. Create and edit environment file:

```bash
cp .env.example .env
```

2. Install backend deps:

```bash
uv sync --locked --group dev
```

3. Install frontend deps:

```bash
npm install
```

4. Build frontend assets:

```bash
npm run build
```

5. Run Django migrations and start app:

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

Optional: run asset watch mode during development:

```bash
npm run dev
```

## Local Run (Docker)

```bash
docker compose up --build
```

Default exposed ports:

- App: `http://localhost` (via nginx)
- Flower: `http://localhost:5555`
