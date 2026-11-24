
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install required system dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libssl-dev \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Install dependencies and upgrade packaging tools
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    python -m pip install --no-cache-dir --upgrade \
        "setuptools>=78.1.1" wheel && \
    python -m pip check

# Verify setuptools version and remove obsolete metadata
RUN python - <<'PY'
import importlib.metadata as metadata
from pathlib import Path
import shutil

version = metadata.version("setuptools")
print(f"Installed setuptools version: {version}")

site_packages = Path(metadata.distribution("setuptools").locate_file(""))

for path in site_packages.glob("setuptools-*.dist-info"):
    if path.name != f"setuptools-{version}.dist-info":
        print(f"Removing obsolete metadata: {path}")
        shutil.rmtree(path)
PY

# Remove pip's bundled SBOM metadata that can cause Trivy
# to report an outdated setuptools version (70.3.0)
RUN rm -f /usr/local/lib/python3.12/site-packages/pip/_vendor/bom.cdx.json

# Copy application files
COPY . .

# Create non-root user
RUN groupadd -r appgroup && \
    useradd -r -g appgroup appuser && \
    chown -R appuser:appgroup /app

USER appuser

# Application health check
HEALTHCHECK --interval=30s --timeout=30s \
    --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Initialize database and start FastAPI
CMD ["sh", "-c", "python -m app.database_init && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"]
