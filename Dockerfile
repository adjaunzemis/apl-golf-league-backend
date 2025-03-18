FROM python:3.12@sha256:85ec4fe2a3f8ccac3315795f80c1cd2ef1ac496e892729548c716b120ea2c46a
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:d25a9b42ecc3aac0d63782654dcb2ab4b304f86357794b05a5c39b17f4777339 /uv /uvx /bin/

ARG VERSION=v0.0.0
COPY ./pyproject.toml pyproject.toml
RUN sed -i "s/^version = .*/version = \"${VERSION}\"/" pyproject.toml

COPY ./uv.lock uv.lock
RUN uv sync --frozen

COPY ./app /app/

ENV PATH="/.venv/bin:$PATH"
CMD ["python", "-m", "app.main"]
