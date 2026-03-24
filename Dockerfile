# ---------- Builder ----------
FROM python:3.12-slim AS builder

# Install build dependencies (only needed here)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock ./

ARG VERSION=v0.0.0
RUN sed -i "s/^version = .*/version = \"${VERSION}\"/" pyproject.toml

# Create virtualenv + install deps
RUN uv sync --frozen

# ---------- Runtime ----------
FROM python:3.12-slim

# Install only runtime dependency for postgres
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /.venv /.venv

# Copy application code (small, changes often)
COPY ./app /app/
COPY ./alembic.ini /alembic.ini
COPY ./migrations /migrations

ENV PATH="/.venv/bin:$PATH"

CMD ["python", "-m", "app.main"]
