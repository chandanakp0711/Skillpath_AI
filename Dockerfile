# ===========================================================================
#  SkillPath AI — container image
#  Build:  docker build -t skillpath .
#  Run:    docker run -p 8501:8501 skillpath
# ===========================================================================
FROM python:3.11-slim

# System deps for scientific Python wheels are already bundled; keep it slim.
WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Train the models at build time if artefacts are not committed.
RUN python train.py || true

EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
