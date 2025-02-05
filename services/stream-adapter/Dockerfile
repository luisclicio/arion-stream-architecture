# Based on https://github.com/orgs/python-poetry/discussions/1879
FROM python:3.12-slim AS base
RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential ffmpeg wait-for-it
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN python3 -m venv $POETRY_HOME && \
    $POETRY_HOME/bin/pip install poetry==1.8

FROM base AS common
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry run pip install --upgrade pip setuptools wheel

FROM common AS development
RUN poetry install --no-root
COPY . .
CMD ["poetry", "run", "python", "-m", "src.main"]

FROM common AS production
RUN poetry install --no-root --without dev
COPY . .
CMD ["poetry", "run", "python", "-m", "src.main"]
