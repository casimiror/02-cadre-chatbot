# Stage 1: build the React app
FROM node:24-slim AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: python runtime with uv
FROM python:3.12-slim AS runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY backend/pyproject.toml backend/uv.lock* ./
RUN uv sync --no-dev --no-install-project
COPY backend/ ./
COPY --from=frontend /frontend/dist /app/static
ENV FRONTEND_DIST=/app/static PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["sh", "-c", "fastapi run --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
