# Use Python 3.12 as base image
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm --version && \
    node --version

# Copy application code
COPY . .

# Install and run tailwindcss directly
RUN npm init -y && \
    npm install tailwindcss postcss autoprefixer && \
    echo "module.exports = {content: ['./**/*.{html,js,py}'],theme: {extend: {},},plugins: [],}" > tailwind.config.js && \
    echo "Processing CSS with tailwindcss..." && \
    npx tailwindcss -i styles/main.css -o static/css/app.css || echo "Warning: Failed to generate CSS"

# Create final image with smaller size
FROM python:3.12-slim

WORKDIR /app

# Install necessary packages in final image
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn tortoise-orm

# Copy application code and generated CSS from builder
COPY --from=builder /app /app

# Create a volume for the database
VOLUME /app/data

# Set environment variables
ENV PYTHONPATH=/app \
    PORT=8000 \
    DB_URL=sqlite://data/db.sqlite3

# Create a non-root user to run the application
RUN useradd -m appuser
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data
USER appuser

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
