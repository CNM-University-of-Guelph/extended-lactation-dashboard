FROM python:3.12-slim

WORKDIR /app

# Declare build arguments
ARG ALLOWED_HOSTS
ARG DEBUG
ARG DJANGO_SECRET_KEY
ARG DATABASE_URL
ARG PGDATABASE
ARG PGUSER
ARG PGPASSWORD
ARG PGHOST
ARG PGPORT
ARG CORS_ALLOWED_ORIGINS
ARG CORS_ALLOW_ALL_ORIGINS
ARG CORS_ALLOWS_CREDENTIALS
ARG CHANNEL_LAYERS_BACKEND
ARG REDIS_URL
ARG BACKEND_URL

# Convert ARGs to ENVs for runtime
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS}
ENV DEBUG=${DEBUG}
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ENV DATABASE_URL=${DATABASE_URL}
ENV PGDATABASE=${PGDATABASE}    
ENV PGUSER=${PGUSER}    
ENV PGPASSWORD=${PGPASSWORD}
ENV PGHOST=${PGHOST}
ENV PGPORT=${PGPORT}
ENV CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS}
ENV CORS_ALLOW_ALL_ORIGINS=${CORS_ALLOW_ALL_ORIGINS}
ENV CORS_ALLOWS_CREDENTIALS=${CORS_ALLOWS_CREDENTIALS}
ENV CHANNEL_LAYERS_BACKEND=${CHANNEL_LAYERS_BACKEND}
ENV REDIS_URL=${REDIS_URL}
ENV BACKEND_URL=${BACKEND_URL}

# Install dependencies
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY backend/ .

# Make sure migrations and static files are handled
RUN python manage.py collectstatic --noinput

# Railway will provide the PORT environment variable
CMD python manage.py migrate && \
    gunicorn backend.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --timeout 300 \
    --workers 3 \
    --threads 3 \
    --worker-class gthread 