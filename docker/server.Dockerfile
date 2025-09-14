# Dockerfile for running AdventOfCodeJudge server
FROM python:3.11-slim

# Install Python dependencies
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy server sources and dataset
COPY server /app/server
COPY data /app/data

# Environment defaults
ENV AOCJUDGE_HOST=0.0.0.0 \
    AOCJUDGE_PORT=8000

EXPOSE 8000
CMD ["python", "server/main.py"]
