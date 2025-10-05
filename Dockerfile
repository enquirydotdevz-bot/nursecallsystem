# -------------------------------
# STEP 1: Base image
# -------------------------------
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -------------------------------
# STEP 2: Set working directory
# -------------------------------
WORKDIR /app

# -------------------------------
# STEP 3: Install system dependencies
# -------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# STEP 4: Install Python dependencies
# -------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# -------------------------------
# STEP 5: Copy project files
# -------------------------------
COPY . .

# -------------------------------
# STEP 6: Setup environment
# -------------------------------
ENV DJANGO_SETTINGS_MODULE=core.settings
ENV PYTHONPATH=/app

# -------------------------------
# STEP 7: Expose port
# -------------------------------
EXPOSE 8000

# -------------------------------
# -------------------------------
# STEP 8: Entrypoint: Migrate, collectstatic, create superuser, start server
# -------------------------------
ENV DJANGO_SUPERUSER_USERNAME=mudit1
ENV DJANGO_SUPERUSER_EMAIL=bhojakmudit26@gmail.com
ENV DJANGO_SUPERUSER_PASSWORD=9314110690

CMD bash -c "\
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL && \
    gunicorn core.wsgi:application --bind 0.0.0.0:8000 \
"

