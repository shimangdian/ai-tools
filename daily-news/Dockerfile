FROM python:3.11-slim

WORKDIR /app

# Install Node.js and npm for Tesseract.js
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Verify Node.js and npm installation
RUN node --version && npm --version

# Copy Node.js dependencies and install
COPY package.json package-lock.json* ./
RUN npm install

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY ocr_service.js .
COPY config.yaml .

# Create log directory
RUN mkdir -p /app/logs

# Run the application
CMD ["python", "-m", "app.main"]
