# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	libpq-dev \
	gettext \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

# Create and set work directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock /app/

# Install Python dependencies
RUN poetry install --no-root

# Copy the application code
COPY . /app/

# Collect static files
RUN poetry run python manage.py collectstatic --noinput

# Run database migrations
RUN poetry run python manage.py migrate

# Expose the port
EXPOSE 8000

# Start the Gunicorn server
CMD ["poetry", "run", "gunicorn", "--config", "gunicorn.conf.py", "backend.wsgi:application"]