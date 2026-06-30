# --- Builder Stage ---
FROM dartfx/docker-api-base:latest AS builder

USER root

# Install git and ca-certificates to clone repositories
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project configuration files first to optimize layer caching
COPY pyproject.toml ./

# Install project dependencies into the virtual environment /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install --no-cache -r pyproject.toml

# Copy project source code
COPY . /app

# Install the project itself (without reinstalling dependencies)
RUN uv pip install --no-cache --no-deps .

# --- Runtime Stage ---
FROM dartfx/docker-api-base:latest
WORKDIR /app

# Copy the updated virtual environment and application code with proper ownership
COPY --from=builder --chown=appuser:appgroup /opt/venv /opt/venv
COPY --chown=appuser:appgroup . /app

# Add virtual environment to PATH and set PYTHONPATH so fairproxy_api imports resolve correctly
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app/src/dartfx

# Run as the default non-root user
USER appuser

# Expose default FastAPI/uvicorn port
EXPOSE 8000

# Start the service entrypoint
CMD ["uvicorn", "fairproxy_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
