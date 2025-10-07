# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_HOME="" \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY main.py ./
COPY src ./src
COPY backend ./backend
COPY deploy ./deploy
COPY docs ./docs

RUN pip install --upgrade pip \
    && pip install --no-cache-dir . \
    && pip install uvicorn[standard] fastapi websockets python-multipart python-jose[cryptography] passlib[bcrypt]

ENV PYTHONPATH=${APP_HOME}/src
