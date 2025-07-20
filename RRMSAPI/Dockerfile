FROM python:3.13.5

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev curl netcat-openbsd gcc

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the project files
COPY . .

# Copy .env file (optional, for build-time context)
# Uncomment if you want to use .env during build
# COPY .env ./

# Collect static files (make sure required ENV vars like DB_NAME are set if needed)
# These values must be defined in your .env or passed with `--build-arg` or `ENV`
RUN python manage.py collectstatic --noinput || echo "Collect static failed, skipping..."

# Expose port
EXPOSE 8000

# Run the server
CMD ["gunicorn", "RRMSAPI.wsgi:application", "--bind", "0.0.0.0:8000"]
