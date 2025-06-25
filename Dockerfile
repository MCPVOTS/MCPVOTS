# Use official Node.js LTS image as base
FROM node:18-alpine AS base

# Set working directory
WORKDIR /app

# Add labels for better container management
LABEL maintainer="MCPVots Development Team"
LABEL version="1.0.0"
LABEL description="Advanced Model Context Protocol Integration Platform"

# Install system dependencies for compilation
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    cairo-dev \
    jpeg-dev \
    pango-dev \
    musl-dev \
    giflib-dev \
    pixman-dev \
    pangomm-dev \
    libjpeg-turbo-dev \
    freetype-dev

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S mcpvots -u 1001

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./
COPY vite.config.ts ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Development stage
FROM base AS development
ENV NODE_ENV=development
RUN npm ci
COPY . .
EXPOSE 3000
USER mcpvots
CMD ["npm", "run", "dev"]

# Build stage
FROM base AS builder
ENV NODE_ENV=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS production

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create app directory and user
WORKDIR /app
RUN addgroup -g 1001 -S nodejs && \
    adduser -S mcpvots -u 1001

# Copy built application from builder stage
COPY --from=builder --chown=mcpvots:nodejs /app/dist ./dist
COPY --from=builder --chown=mcpvots:nodejs /app/package*.json ./
COPY --from=builder --chown=mcpvots:nodejs /app/node_modules ./node_modules

# Copy configuration files
COPY --chown=mcpvots:nodejs config/ ./config/
COPY --chown=mcpvots:nodejs ecosystem_builder.py ./
COPY --chown=mcpvots:nodejs ecosystem_manager.py ./
COPY --chown=mcpvots:nodejs advanced_orchestrator.py ./

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/backups && \
    chown -R mcpvots:nodejs /app/data /app/logs /app/backups

# Set environment variables
ENV NODE_ENV=production \
    PORT=3000 \
    HOST=0.0.0.0 \
    LOG_LEVEL=info \
    METRICS_RETENTION_DAYS=7

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node dist/healthcheck.js || exit 1

# Switch to non-root user
USER mcpvots

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start the application
CMD ["node", "dist/server.js"]
