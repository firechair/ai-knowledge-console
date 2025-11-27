# frontend.Dockerfile
# ====================
#
# Multi-stage build: Node for building, Nginx for serving
# Final image: ~50MB

# ===========================================================================
# Stage 1: Build React App
# ===========================================================================
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files first (better caching)
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --silent

# Copy source code
COPY frontend/ .

# Set environment variable for production API URL
# This will be proxied through nginx to the backend
ENV VITE_API_URL=/api

# Build the application
RUN npm run build

# ===========================================================================
# Stage 2: Production with Nginx
# ===========================================================================
FROM nginx:alpine as production

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Install curl for healthcheck
RUN apk add --no-cache curl

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
