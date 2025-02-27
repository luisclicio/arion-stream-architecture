FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:0.5.28 /uv /uvx /bin/

FROM base AS common
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

FROM common AS development
COPY . .
CMD ["fastapi", "dev", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]

FROM common AS production
RUN uv sync --frozen --no-dev
COPY . .
CMD ["fastapi", "run", "src/main.py", "--port", "8000"]
