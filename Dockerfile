FROM python:3.12@sha256:2e726959b8df5cd9fd95a4cbd6dcd23d8a89e750e9c2c5dc077ba56365c6a925
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:a0c0e6aed043f5138957ea89744536eed81f1db633dc9bb3be2b882116060be2 /uv /uvx /bin/

ARG VERSION=development
COPY ./pyproject.toml pyproject.toml
RUN sed -i "s/^version = .*/version = \"${VERSION}\"/" pyproject.toml

COPY ./uv.lock uv.lock
RUN uv sync --frozen

COPY ./app /app/

ENV PATH="/.venv/bin:$PATH"
CMD ["python", "-m", "app.main"]
