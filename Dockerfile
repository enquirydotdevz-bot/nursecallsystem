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
# STEP 7: Run collectstatic
# -------------------------------
RUN python manage.py collectstatic --noinput

# -------------------------------
# STEP 8: Expose port and run
# -------------------------------
EXPOSE 8000

# Default command: Gunicorn for Django
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
