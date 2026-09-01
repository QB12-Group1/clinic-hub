# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/usr/local

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

FROM base AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .
RUN uv sync --frozen --no-dev

FROM base AS runtime
RUN groupadd --system app && useradd --system --gid app --create-home app

COPY --from=build /usr/local /usr/local
COPY --chown=app:app . .

RUN mkdir -p /app/staticfiles /app/media && chown -R app:app /app/staticfiles /app/media

RUN chmod +x docker/entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["uvicorn", "core.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
