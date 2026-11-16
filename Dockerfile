# ---------- Builder ----------
FROM python:3.15-slim@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928 AS builder

# Install build dependencies (only needed here)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:5cc1805e2426484abca4ad46ea783bab281fdb225fd82d8ce6d66a81254bac85 /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock ./

ARG VERSION=v0.0.0
RUN sed -i "s/^version = .*/version = \"${VERSION}\"/" pyproject.toml

# Install dependencies into /app/.venv
RUN uv sync --frozen

# ---------- Runtime ----------
FROM python:3.15-slim@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928

# Install runtime dependency for postgres
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /app/.venv /.venv

# Copy application code
COPY ./app /app/app
COPY --from=builder /app/pyproject.toml /app/pyproject.toml
COPY ./alembic.ini /alembic.ini
COPY ./migrations /migrations

ENV PATH="/.venv/bin:$PATH"

CMD ["python", "-m", "app.main"]
