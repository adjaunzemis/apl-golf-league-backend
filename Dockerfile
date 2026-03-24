FROM python:3.12@sha256:c4c9e439bf98d5c20453156194f937aefb4a633555d93a1960d612052c4b3436
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:69e13c7ae3a7649cbe0c912ca8afe00656966622a13f2db2d7eef7bb01118ccf /uv /uvx /bin/

ARG VERSION=v0.0.0
COPY ./pyproject.toml pyproject.toml
RUN sed -i "s/^version = .*/version = \"${VERSION}\"/" pyproject.toml

COPY ./uv.lock uv.lock
RUN uv sync --frozen

COPY ./app /app/
COPY ./alembic.ini /alembic.ini
COPY ./migrations /migrations

ENV PATH="/.venv/bin:$PATH"
CMD ["python", "-m", "app.main"]
