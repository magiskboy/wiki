---
tags:
  - python
date: 2026-05-29
---
# uv - python snippets

## Using uv with docker
```Dockerfile
FROM python:3.13-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
ENV UV_NO_DEV=1
COPY ./pyproject.toml ./uv.lock /app/
RUN uv sync --locked
COPY . /app
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
# you can call executable files what you install via uv directly without uv run ...
CMD ["<exec file>", ...]
```
Notice: add .venv to .dockerignore

## Using uv to create virtualenv within specific python version
```bash
uv venv --python python3.13
```
