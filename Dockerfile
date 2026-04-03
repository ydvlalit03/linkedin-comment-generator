# Combined Dockerfile — FastAPI backend + Next.js frontend in one container

# Stage 1: Build Next.js
FROM node:20-alpine AS frontend-builder
WORKDIR /app

RUN apk add --no-cache python3 make g++

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN mkdir -p data

# Build-time backend URL points to localhost (same container)
ENV BACKEND_URL=http://localhost:8000
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 2: Production
FROM python:3.12-slim

WORKDIR /app

# Install Node.js for Next.js standalone server
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend
COPY backend/ /app/backend/

# Copy Next.js standalone build
COPY --from=frontend-builder /app/.next/standalone /app/frontend/
COPY --from=frontend-builder /app/.next/static /app/frontend/.next/static
COPY --from=frontend-builder /app/public /app/frontend/public

# Create data directory
RUN mkdir -p /app/data /app/backend/data

# Copy start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 3000

CMD ["/app/start.sh"]
