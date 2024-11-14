# Stage 1: Build frontend
FROM node:20-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Build backend and setup nginx
FROM python:3.12-slim

# Install nginx and required system dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Railway environment variables
ARG DJANGO_SECRET_KEY
ARG DEBUG
ARG ALLOWED_HOSTS
ARG CORS_ALLOW_ALL_ORIGINS
ARG CORS_ALLOWED_ORIGINS
ARG CORS_ALLOWS_CREDENTIALS

# Database credentials
ARG DB_ENGINE
ARG DB_NAME
ARG DB_USER
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_PORT

# Channel layers
ARG CHANNEL_LAYERS_BACKEND

# Set environment variables
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ENV DEBUG=${DEBUG}
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS}
ENV DB_ENGINE=${DB_ENGINE}
ENV DB_NAME=${DB_NAME}
ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV CORS_ALLOW_ALL_ORIGINS=${CORS_ALLOW_ALL_ORIGINS}
ENV CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS}
ENV CORS_ALLOWS_CREDENTIALS=${CORS_ALLOWS_CREDENTIALS}
ENV CHANNEL_LAYERS_BACKEND=${CHANNEL_LAYERS_BACKEND}

# Setup backend
WORKDIR /backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ .

# Create necessary directories
RUN mkdir -p media staticfiles

# Copy frontend build from previous stage and nginx config
COPY --from=frontend-build /frontend/dist /var/www/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose ports
EXPOSE 3000 8000

# Start both nginx and Django
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "backend.asgi:application"] 