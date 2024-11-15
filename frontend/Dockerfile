# Build stage
FROM node:18 AS build

WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy the rest of the application
COPY frontend/ .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy the built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy appropriate nginx configuration based on environment
ARG RAILWAY_ENVIRONMENT
COPY frontend/nginx${RAILWAY_ENVIRONMENT:+.conf}${RAILWAY_ENVIRONMENT:-'.dev.conf'} /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]