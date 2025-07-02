FROM python:3.12@sha256:77a36ff63e657d8ec7cd4e86e452f4cd23b6c92811696b0735226fbc0660a5b8
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:69e13c7ae3a7649cbe0c912ca8afe00656966622a13f2db2d7eef7bb01118ccf /uv /uvx /bin/

ARG VERSION=v0.0.0
COPY ./pyproject.toml pyproject.toml
RUN sed -i "s/^version = .*/version = \"${VERSION}\"/" pyproject.toml

COPY ./uv.lock uv.lock
RUN uv sync --frozen

COPY ./app /app/

ENV PATH="/.venv/bin:$PATH"
CMD ["python", "-m", "app.main"]
