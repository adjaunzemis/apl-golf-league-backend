FROM python:3.13.3@sha256:3abe339a3bc81ffabcecf9393445594124de6420b3cfddf248c52b1115218f04
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:cb641b1979723dc5ab87d61f079000009edc107d30ae7cbb6e7419fdac044e9f /uv /uvx /bin/

ARG VERSION=v0.0.0
COPY ./pyproject.toml pyproject.toml
RUN sed -i "s/^version = .*/version = \"${VERSION}\"/" pyproject.toml

COPY ./uv.lock uv.lock
RUN uv sync --frozen

COPY ./app /app/

ENV PATH="/.venv/bin:$PATH"
CMD ["python", "-m", "app.main"]
