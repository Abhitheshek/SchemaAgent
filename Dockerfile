FROM python:3.12-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Start the application
CMD ["python", "main.py"]