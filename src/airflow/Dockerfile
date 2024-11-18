FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
ENV AIRFLOW_HOME=/usr/local/airflow

WORKDIR $AIRFLOW_HOME

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files to the container
COPY . .

# Create entrypoint script
COPY <<EOF /entrypoint.sh
#!/bin/bash
set -e

# Wait for MySQL to be ready
echo "Waiting for MySQL..."
while ! nc -z mysql 3306; do
  sleep 1
done
echo "MySQL is ready!"

# Initialize the database
airflow db migrate

# Create default user if it doesn't exist
airflow users create -u admin -f Admin -l User -r Admin -e admin@example.com -p admin || true

# Start Airflow
airflow scheduler & airflow webserver -p 8080
EOF

RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]