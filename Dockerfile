# SF Bay water temperature Streamlit app
# Build from repo root. Ensure up_to_2024.csv exists (or is mounted at runtime).
FROM python:3.12-slim

WORKDIR /app

# System deps for healthcheck only (PyMySQL is pure Python, no build deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code and data. Ensure up_to_2024.csv is in the repo or mount it at runtime.
COPY . .

# Entrypoint writes secrets from env (e.g. MYSQL_*) then runs the app.
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["streamlit", "run", "baytemps_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
