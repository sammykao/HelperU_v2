# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update \ 
    && apt-get install -y --no-install-recommends curl ca-certificates \ 
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh -s -- -y \ 
    && ln -sf /root/.local/bin/uv /usr/local/bin/uv

# Copy project metadata and install deps
COPY pyproject.toml ./
RUN uv venv && uv sync --no-dev

# Copy application code
COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
