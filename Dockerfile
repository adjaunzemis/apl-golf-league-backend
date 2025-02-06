FROM python:3.12@sha256:2e726959b8df5cd9fd95a4cbd6dcd23d8a89e750e9c2c5dc077ba56365c6a925
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:88d7b48fc9f17462c82b5482e497af250d337f3f14e1ac97c16e68eba49b651e /uv /uvx /bin/

ARG VERSION=v0.0.0
COPY ./pyproject.toml pyproject.toml
RUN sed -i "s/^version = .*/version = \"${VERSION}\"/" pyproject.toml

COPY ./uv.lock uv.lock
RUN uv sync --frozen

COPY ./app /app/

ENV PATH="/.venv/bin:$PATH"
CMD ["python", "-m", "app.main"]
