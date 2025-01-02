FROM python:3.12
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ARG VERSION=development
COPY ./pyproject.toml pyproject.toml
RUN sed -i "s/^version = .*/version = \"${VERSION}\"/" pyproject.toml

COPY ./uv.lock uv.lock
RUN uv sync --frozen

COPY ./app /app/

ENV PATH="/.venv/bin:$PATH"
CMD ["python", "-m", "app.main"]
