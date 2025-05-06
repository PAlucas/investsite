FROM python:3.9-slim

WORKDIR /app

# Install system dependencies required for psycopg2 and debugging
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install debugging tools
RUN pip install --no-cache-dir debugpy watchdog

# Copy application code
COPY . .

# Expose ports for the Flask application and debugger
EXPOSE 5000 5678

# Command to run the application with live reloading and debugging enabled
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "app.py"]
