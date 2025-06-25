# MCPVots Production Deployment Guide

This guide covers deploying MCPVots to various production environments with our advanced technology stack.

## 🚀 Quick Deployment Options

### Option 1: Vercel (Recommended for Frontend)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to Vercel
vercel --prod

# Set environment variables in Vercel dashboard
# Required: NODE_ENV=production, MCP_DEFAULT_SERVER, etc.
```

### Option 2: Docker Deployment

```bash
# Build production image
docker build -t mcpvots:latest .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up --scale web=3 -d
```

### Option 3: Traditional VPS/Cloud Server

```bash
# Clone and setup
git clone https://github.com/kabrony/MCPVots.git
cd MCPVots
npm install --production

# Build for production
NODE_ENV=production npm run build

# Start with PM2
npm install -g pm2
pm2 start ecosystem.config.js --env production
```

## 🐳 Docker Configuration

### Production Dockerfile

Already configured in `Dockerfile` with:
- Multi-stage build for optimization
- Security best practices
- Health checks
- Non-root user
- Optimized caching

### Docker Compose for Production

```yaml
version: '3.8'
services:
  mcpvots:
    build: .
    ports:
      - "80:3000"
    environment:
      - NODE_ENV=production
      - PORT=3000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - mcpvots

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - mcpvots
    networks:
      - mcpvots

networks:
  mcpvots:
    driver: bridge
```

## ⚙️ Environment Configuration

### Production Environment Variables

```bash
# Core application
NODE_ENV=production
PORT=3000
HOST=0.0.0.0

# MCP Configuration
MCP_DEFAULT_SERVER=wss://your-mcp-server.com
MCP_PRIMARY_TOKEN=your_production_token
MCP_RECONNECT_INTERVAL=5000

# Security
SESSION_SECRET=your_super_secure_session_secret_min_32_chars
JWT_SECRET=your_jwt_secret_key_min_256_bits
ENABLE_TLS=true

# Monitoring
LOG_LEVEL=warn
METRICS_RETENTION_DAYS=30
ENABLE_PERFORMANCE_MONITORING=true

# Trilogy AGI
TRILOGY_ENABLED=true
AI_OPTIMIZATION_ENABLED=true
AI_MEMORY_PERSISTENCE=redis

# Database (if using PostgreSQL)
DATABASE_URL=postgresql://user:pass@localhost:5432/mcpvots
REDIS_URL=redis://localhost:6379

# Backup
BACKUP_ENABLED=true
BACKUP_S3_ENABLED=true
BACKUP_S3_BUCKET=mcpvots-backups
```

## 🔒 SSL/TLS Configuration

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name mcpvots.app www.mcpvots.app;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mcpvots.app www.mcpvots.app;

    ssl_certificate /etc/ssl/certs/mcpvots.crt;
    ssl_certificate_key /etc/ssl/certs/mcpvots.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://mcpvots:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /ws {
        proxy_pass http://mcpvots:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 📊 Monitoring & Logging

### Production Logging

```javascript
// Configure structured logging
{
  "logging": {
    "level": "warn",
    "format": "json",
    "outputs": [
      {
        "type": "file",
        "filename": "/app/logs/mcpvots.log",
        "maxSize": "50MB",
        "maxFiles": 10,
        "compress": true
      },
      {
        "type": "syslog",
        "host": "logs.example.com",
        "port": 514
      }
    ]
  }
}
```

### Health Checks

```bash
# Application health endpoint
curl -f https://mcpvots.app/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-06-24T01:30:00.000Z",
  "version": "1.0.0",
  "uptime": 86400,
  "memory": {
    "used": "128MB",
    "free": "384MB"
  },
  "services": {
    "mcp": "connected",
    "database": "connected",
    "redis": "connected"
  }
}
```

## 🔧 Performance Optimization

### Production Build Optimization

```json
{
  "build": {
    "optimization": {
      "minify": true,
      "compress": true,
      "splitChunks": true,
      "treeshaking": true
    },
    "target": "es2020",
    "bundleAnalyzer": false
  }
}
```

### Caching Strategy

```javascript
// Cache configuration
{
  "cache": {
    "static": {
      "maxAge": "1y",
      "immutable": true
    },
    "api": {
      "maxAge": "5m",
      "staleWhileRevalidate": "1h"
    },
    "cdn": {
      "enabled": true,
      "baseUrl": "https://cdn.mcpvots.app"
    }
  }
}
```

## 🚨 Backup & Recovery

### Automated Backup

```bash
#!/bin/bash
# backup.sh - Production backup script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mcpvots"
APP_DIR="/app"

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Backup application data
tar -czf $BACKUP_DIR/$DATE/data.tar.gz $APP_DIR/data/
tar -czf $BACKUP_DIR/$DATE/config.tar.gz $APP_DIR/config/
tar -czf $BACKUP_DIR/$DATE/logs.tar.gz $APP_DIR/logs/

# Upload to S3 (if configured)
if [ "$BACKUP_S3_ENABLED" = "true" ]; then
    aws s3 sync $BACKUP_DIR/$DATE s3://$BACKUP_S3_BUCKET/$DATE/
fi

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -type d -mtime +30 -exec rm -rf {} +

echo "Backup completed: $DATE"
```

### Recovery Process

```bash
#!/bin/bash
# restore.sh - Recovery script

BACKUP_DATE=$1
BACKUP_DIR="/backups/mcpvots"

if [ -z "$BACKUP_DATE" ]; then
    echo "Usage: ./restore.sh YYYYMMDD_HHMMSS"
    exit 1
fi

# Stop application
docker-compose down

# Restore data
tar -xzf $BACKUP_DIR/$BACKUP_DATE/data.tar.gz -C /
tar -xzf $BACKUP_DIR/$BACKUP_DATE/config.tar.gz -C /

# Start application
docker-compose up -d

echo "Recovery completed from: $BACKUP_DATE"
```

## 🔄 CI/CD Pipeline

### GitHub Actions Production Deploy

```yaml
name: Production Deployment

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18.x'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test
    
    - name: Build application
      run: npm run build
    
    - name: Deploy to production
      run: |
        # Your deployment script here
        # Examples: rsync, docker push, kubectl apply, etc.
```

## 📈 Scaling Configuration

### Horizontal Scaling

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcpvots
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcpvots
  template:
    metadata:
      labels:
        app: mcpvots
    spec:
      containers:
      - name: mcpvots
        image: mcpvots:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: mcpvots-service
spec:
  selector:
    app: mcpvots
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

## 🔍 Troubleshooting

### Common Issues

1. **WebSocket Connection Failures**
   ```bash
   # Check firewall rules
   sudo ufw status
   
   # Verify WebSocket proxy configuration
   nginx -t
   ```

2. **High Memory Usage**
   ```bash
   # Monitor memory usage
   docker stats
   
   # Check for memory leaks
   node --inspect app.js
   ```

3. **SSL Certificate Issues**
   ```bash
   # Verify certificate validity
   openssl x509 -in certificate.crt -text -noout
   
   # Check certificate chain
   openssl verify -CAfile ca-bundle.crt certificate.crt
   ```

### Performance Debugging

```bash
# Enable Node.js profiling
NODE_OPTIONS="--max-old-space-size=4096 --inspect" npm start

# Monitor application metrics
curl https://mcpvots.app/metrics

# Check logs for errors
tail -f /app/logs/mcpvots.log | grep ERROR
```

## 📞 Support

For production deployment support:
- GitHub Issues: https://github.com/kabrony/MCPVots/issues
- Documentation: https://github.com/kabrony/MCPVots/wiki
- Security Issues: Follow SECURITY.md guidelines

---

**Production deployment successful!** 🎉

Your MCPVots platform is now running with enterprise-grade reliability and our advanced technology stack.
