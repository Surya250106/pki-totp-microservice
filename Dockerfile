# ================================
# Stage 1: Builder
# ================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies (if any heavy libs later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (better layer caching)
COPY requirements.txt .

# Create virtualenv and install dependencies into it
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install -r requirements.txt


# ================================
# Stage 2: Runtime
# ================================
FROM python:3.11-slim AS runtime

# ---------- Timezone + cron ----------
ENV TZ=UTC

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
 && rm -rf /var/lib/apt/lists/* \
 && ln -fs /usr/share/zoneinfo/UTC /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv

# Use venv Python by default
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    SEED_FILE_PATH=/data/seed.txt

WORKDIR /app

# Copy application code (FastAPI app, scripts, keys, etc.)
COPY . .

# Create volume mount points and set permissions
RUN mkdir -p /data /cron \
 && chmod 755 /data /cron

# Install cron job configuration
# (cron/2fa-cron will be created in STEP 10 and must have LF line endings)
COPY cron/2fa-cron /etc/cron.d/2fa-cron

# Cron files must have 0644 perms and be registered
RUN chmod 0644 /etc/cron.d/2fa-cron \
 && crontab /etc/cron.d/2fa-cron

# Expose FastAPI port
EXPOSE 8080

# Start cron daemon and API server when container launches
CMD cron && uvicorn app.main:app --host 0.0.0.0 --port 8080
