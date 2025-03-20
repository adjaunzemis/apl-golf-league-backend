FROM python:3.12@sha256:4e7024df2f2099e87d0a41893c299230d2a974c3474e681b0996f141951f9817
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:d25a9b42ecc3aac0d63782654dcb2ab4b304f86357794b05a5c39b17f4777339 /uv /uvx /bin/

ARG VERSION=v0.0.0
COPY ./pyproject.toml pyproject.toml
RUN sed -i "s/^version = .*/version = \"${VERSION}\"/" pyproject.toml

COPY ./uv.lock uv.lock
RUN uv sync --frozen

COPY ./app /app/

ENV PATH="/.venv/bin:$PATH"
CMD ["python", "-m", "app.main"]
