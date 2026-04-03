# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app

# better-sqlite3 needs build tools
RUN apk add --no-cache python3 make g++

COPY package.json package-lock.json* ./
RUN npm ci

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app

RUN apk add --no-cache python3 make g++

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Create data directory for SQLite
RUN mkdir -p data

# Build Next.js
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 3: Production
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# better-sqlite3 needs these at runtime
RUN apk add --no-cache libstdc++

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built app
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Create data directory for SQLite (writable by nextjs user)
RUN mkdir -p data && chown nextjs:nodejs data

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
