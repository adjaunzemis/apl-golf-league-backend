# ---------- Builder ----------
FROM python:3.12-slim@sha256:3d5ed973e45820f5ba5e46bd065bd88b3a504ff0724d85980dcd05eab361fcf4 AS builder

# Install build dependencies (only needed here)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:e49fde5daf002023f0a2e2643861ce9ca8a8da5b73d0e6db83ef82ff99969baf /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock ./

ARG VERSION=v0.0.0
RUN sed -i "s/^version = .*/version = \"${VERSION}\"/" pyproject.toml

# Install dependencies into /app/.venv
RUN uv sync --frozen

# ---------- Runtime ----------
FROM python:3.12-slim@sha256:3d5ed973e45820f5ba5e46bd065bd88b3a504ff0724d85980dcd05eab361fcf4

# Install runtime dependency for postgres
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /app/.venv /.venv

# Copy application code
COPY ./app /app/app
COPY ./pyproject.toml /app/pyproject.toml
COPY ./alembic.ini /alembic.ini
COPY ./migrations /migrations

ENV PATH="/.venv/bin:$PATH"

CMD ["python", "-m", "app.main"]
