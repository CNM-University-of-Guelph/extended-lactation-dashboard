# Stage 1: Build frontend
FROM node:20-slim as frontend-build
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

# Create startup script
RUN echo '#!/bin/bash\n\
nginx\n\
python manage.py runserver 0.0.0.0:8000\n\
' > /start.sh && chmod +x /start.sh

# Expose ports
EXPOSE 3000 8000

# Start both nginx and Django
CMD ["/start.sh"] 