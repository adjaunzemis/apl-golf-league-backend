FROM python:3.12@sha256:11e5de79af775dc79e765116bfd2cd574e3ba0bc0aa87c29bb3ef7b8d03194bb
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:563b73ab264117698521303e361fb781a0b421058661b4055750b6c822262d1e /uv /uvx /bin/

ARG VERSION=v0.0.0
COPY ./pyproject.toml pyproject.toml
RUN sed -i "s/^version = .*/version = \"${VERSION}\"/" pyproject.toml

COPY ./uv.lock uv.lock
RUN uv sync --frozen

COPY ./app /app/

ENV PATH="/.venv/bin:$PATH"
CMD ["python", "-m", "app.main"]
