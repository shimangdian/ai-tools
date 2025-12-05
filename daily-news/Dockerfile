FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY config.yaml .

# Create log directory
RUN mkdir -p /app/logs

# Run the application
CMD ["python", "-m", "app.main"]
