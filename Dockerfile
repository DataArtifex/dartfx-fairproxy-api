# Use a multi-stage build for a small final image
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Set the working directory to the project root
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy the project files (including pyproject.toml, uv.lock, and src)
# Build this from the project root: docker build -f infrastructure/Dockerfile .
COPY . /app

# Sync the project and its dependencies
# Since we are building from the project directory, uv will fetch
# toolkit dependencies from GitHub as specified in pyproject.toml.
RUN uv sync --no-dev

# --- Production Stage ---
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy the environment from the builder
COPY --from=builder /app /app

# Ensure the app environment is on the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose the FastAPI port
EXPOSE 8000

# Production command: Gunicorn with Uvicorn workers
CMD ["gunicorn", \
     "-w", "4", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--chdir", "src/dartfx", \
     "fairproxy_api.main:app"]
