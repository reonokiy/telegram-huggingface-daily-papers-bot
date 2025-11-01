# HuggingFace Daily Papers Telegram Bot
# Multi-stage build for optimized Python application

# Stage 1: Builder - Install dependencies
FROM python:3.12-slim AS builder

# Install uv for faster dependency management
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN uv sync --no-dev

# Stage 2: Runtime - Create minimal image
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 botuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY hf.py cache.py storage.py main.py config.py ./

# Create data directory and set permissions
RUN mkdir -p /app/data && \
    chown -R botuser:botuser /app

# Switch to non-root user
USER botuser

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=5m --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the bot
CMD ["python", "main.py"]
