FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY worker.py .

# Create upload directory
RUN mkdir -p /tmp/uploads

EXPOSE 8003

# Default command (API server)
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8003"]
