# Dockerfile for pmake-recover CI/CD Testing
# Multi-stage build for efficient testing environment

# Build stage
FROM python:3.12-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

# Add metadata
LABEL maintainer="pmake-recover team" \
      org.opencontainers.image.created=$BUILD_DATE \
      org.opencontainers.image.url="https://github.com/pmake-recover/pmake-recover" \
      org.opencontainers.image.source="https://github.com/pmake-recover/pmake-recover" \
      org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.revision=$VCS_REF \
      org.opencontainers.image.vendor="pmake-recover team" \
      org.opencontainers.image.title="pmake-recover" \
      org.opencontainers.image.description="Secure password generation and recovery system - Testing Environment" \
      org.opencontainers.image.documentation="https://github.com/pmake-recover/pmake-recover/blob/main/README.md" \
      org.opencontainers.image.licenses="MIT"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libxml2-utils \
    xmlstarlet \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt

# Runtime stage
FROM python:3.12-slim as runtime

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    libxml2-utils \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r pmake && useradd -r -g pmake pmake

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy project files
COPY --chown=pmake:pmake . .

# Create necessary directories with correct permissions
RUN mkdir -p test-results reports badges files && \
    chown -R pmake:pmake /app && \
    chmod 700 files

# Make scripts executable
RUN chmod +x scripts/*.sh

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

# Switch to non-root user
USER pmake

# Default command runs the full test suite
CMD ["make", "ci-full"]

# Testing stage (extends runtime)
FROM runtime as testing

# Install additional testing tools
USER root
RUN pip install --no-cache-dir \
    pytest-benchmark \
    pytest-profiling \
    pytest-monitor \
    pytest-random-order

USER pmake

# Command for running specific test types
CMD ["pytest", "tests/", "--verbose", "--cov=.", "--cov-report=xml", "--junit-xml=test-results/junit.xml"]

# Security scanning stage
FROM runtime as security

USER root

# Install security scanning tools
RUN pip install --no-cache-dir \
    bandit[toml] \
    safety \
    semgrep \
    pip-audit

USER pmake

# Command for security scanning
CMD ["make", "security-scan"]

# Development stage (includes dev tools)
FROM runtime as development

USER root

# Install development tools
RUN pip install --no-cache-dir \
    ipython \
    ipdb \
    jupyter \
    pre-commit

# Install additional system tools for development
RUN apt-get update && apt-get install -y \
    vim \
    nano \
    htop \
    && rm -rf /var/lib/apt/lists/*

USER pmake

# Expose port for Jupyter (if needed)
EXPOSE 8888

# Command for development environment
CMD ["bash"]

# Production stage (minimal runtime)
FROM python:3.12-slim as production

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r pmake && useradd -r -g pmake pmake

# Copy only runtime virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy only necessary application files
COPY --chown=pmake:pmake makepin.py recoverpin.py helpers.py words.py ./
COPY --chown=pmake:pmake words.txt ./
COPY --chown=pmake:pmake showpass.sh ./

# Create files directory
RUN mkdir -p files && \
    chown pmake:pmake files && \
    chmod 700 files

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER pmake

# Health check for production
HEALTHCHECK --interval=60s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import makepin, recoverpin, helpers, words; print('OK')" || exit 1

# Default production command
CMD ["python", "makepin.py", "--help"]