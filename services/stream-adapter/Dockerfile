FROM python:3.12-slim AS base
RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential ffmpeg wait-for-it
COPY --from=ghcr.io/astral-sh/uv:0.5.28 /uv /uvx /bin/

FROM base AS common
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
ENV PATH="/app/.venv/bin:$PATH"

FROM common AS development
COPY . .
CMD ["python", "-m", "src.main"]

FROM common AS production
RUN uv sync --frozen --no-dev
COPY . .
CMD ["python", "-m", "src.main"]
