# Deployment Guide

This guide covers various deployment strategies for Kairos, from development to production environments.

## 🚀 Quick Deployment Options

### 1. Docker (Recommended)
- **Best for**: Development and production
- **Setup time**: 5 minutes
- **Complexity**: Low

### 2. Manual Deployment
- **Best for**: Custom environments
- **Setup time**: 15-30 minutes
- **Complexity**: Medium

### 3. Cloud Deployment
- **Best for**: Production scaling
- **Setup time**: 30-60 minutes
- **Complexity**: High

## 🐳 Docker Deployment

### Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/kairos.git
cd kairos

# Copy environment variables
cp env.example .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Environment

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Update services
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### Docker Configuration

#### Development (`docker-compose.yml`)
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: kairos
      POSTGRES_USER: kairos_user
      POSTGRES_PASSWORD: kairos_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://kairos_user:kairos_password@postgres:5432/kairos
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
```

#### Production (`docker-compose.prod.yml`)
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      DATABASE_URL: ${DATABASE_URL}
      GITHUB_CLIENT_SECRET: ${GITHUB_CLIENT_SECRET}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - postgres
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL}
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

## 🛠️ Manual Deployment

### Prerequisites
- Python 3.11+ with uv
- Node.js 18+ with npm
- PostgreSQL 15+
- Nginx (for production)
- SSL certificates (for HTTPS)

### Backend Deployment

```bash
# 1. Clone and setup
git clone https://github.com/your-username/kairos.git
cd kairos/backend

# 2. Install dependencies
uv sync --no-dev

# 3. Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/kairos"
export GITHUB_CLIENT_ID="your_client_id"
export GITHUB_CLIENT_SECRET="your_client_secret"
export OPENAI_API_KEY="your_openai_key"

# 4. Run migrations
uv run python migrate.py

# 5. Start production server
uv run gunicorn src.kairos_backend.app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Frontend Deployment

```bash
# 1. Setup frontend
cd ../frontend

# 2. Install dependencies
npm ci --only=production

# 3. Set environment variables
export NEXT_PUBLIC_API_URL="https://api.yourdomain.com"
export NEXT_PUBLIC_GITHUB_CLIENT_ID="your_client_id"

# 4. Build for production
npm run build

# 5. Start production server
npm start
```

### Database Setup

```sql
-- Create database and user
CREATE DATABASE kairos;
CREATE USER kairos_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE kairos TO kairos_user;

-- Create extensions (if needed)
\c kairos
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/kairos
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support (if needed)
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS with Fargate

1. **Build and push Docker images**:
```bash
# Build images
docker build -t kairos-backend ./backend
docker build -t kairos-frontend ./frontend

# Tag for ECR
docker tag kairos-backend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/kairos-backend:latest
docker tag kairos-frontend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/kairos-frontend:latest

# Push to ECR
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/kairos-backend:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/kairos-frontend:latest
```

2. **Create ECS Task Definition**:
```json
{
  "family": "kairos-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "kairos-backend",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/kairos-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/kairos"
        }
      ]
    },
    {
      "name": "kairos-frontend",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/kairos-frontend:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ]
    }
  ]
}
```

3. **Create ECS Service**:
```bash
aws ecs create-service \
  --cluster kairos-cluster \
  --service-name kairos-service \
  --task-definition kairos-app:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### Google Cloud Platform

#### Using Cloud Run

1. **Deploy Backend**:
```bash
# Build and deploy backend
gcloud run deploy kairos-backend \
  --source ./backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=$DATABASE_URL
```

2. **Deploy Frontend**:
```bash
# Build and deploy frontend
gcloud run deploy kairos-frontend \
  --source ./frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_URL=$BACKEND_URL
```

### Digital Ocean App Platform

Create `app.yaml`:
```yaml
name: kairos
services:
- name: backend
  source_dir: backend
  build_command: uv sync
  run_command: uv run uvicorn src.kairos_backend.app:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    value: ${kairos-db.DATABASE_URL}
  - key: GITHUB_CLIENT_SECRET
    value: ${GITHUB_CLIENT_SECRET}
    type: SECRET

- name: frontend
  source_dir: frontend
  build_command: npm ci && npm run build
  run_command: npm start
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: NEXT_PUBLIC_API_URL
    value: ${backend.PUBLIC_URL}

databases:
- name: kairos-db
  engine: PG
  num_nodes: 1
  size: db-s-dev-database
```

## 🔧 Environment Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/kairos

# Authentication
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
JWT_SECRET_KEY=your_jwt_secret_key

# AI Features
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Security
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=INFO
```

#### Frontend (.env.local)
```env
# API Configuration
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Authentication
NEXT_PUBLIC_GITHUB_CLIENT_ID=your_github_client_id
NEXT_PUBLIC_GITHUB_REDIRECT_URI=https://yourdomain.com/login

# Analytics (optional)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn

# Feature Flags
NEXT_PUBLIC_ENABLE_AI_FEATURES=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

### Security Configuration

#### Production Security Checklist
- [ ] Use HTTPS everywhere
- [ ] Set secure environment variables
- [ ] Configure CORS properly
- [ ] Use strong passwords and secrets
- [ ] Enable database SSL
- [ ] Set up proper firewall rules
- [ ] Configure security headers
- [ ] Enable logging and monitoring
- [ ] Regular security updates
- [ ] Backup strategy in place

#### Security Headers (Nginx)
```nginx
# Security Headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## 📊 Monitoring and Logging

### Application Monitoring

#### Backend Monitoring
```python
# Add to main.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Sentry configuration
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[
        FastApiIntegration(auto_enabling=True),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=1.0,
)

# Logging configuration
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### Frontend Monitoring
```typescript
// lib/monitoring.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 1.0,
});

// Track user interactions
export const trackEvent = (eventName: string, properties?: any) => {
  Sentry.addBreadcrumb({
    message: eventName,
    data: properties,
    level: 'info',
  });
};
```

### Health Checks

#### Backend Health Check
```python
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0",
            "services": {
                "database": "healthy",
                "api": "healthy"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )
```

### Logging Strategy

#### Structured Logging
```python
import structlog
import logging

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage
logger.info("Event created", event_id=event.id, user_id=user.id)
logger.error("Scheduling conflict", event_id=event.id, conflict_reason="overlap")
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install uv
        run: pip install uv
      
      - name: Test Backend
        run: |
          cd backend
          uv sync --dev
          uv run pytest
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Test Frontend
        run: |
          cd frontend
          npm ci
          npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Production
        run: |
          # Deploy script here
          ./scripts/deploy.sh production
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          GITHUB_CLIENT_SECRET: ${{ secrets.GITHUB_CLIENT_SECRET }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## 🔄 Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# scripts/backup.sh

# Create backup
pg_dump $DATABASE_URL > "backup-$(date +%Y%m%d-%H%M%S).sql"

# Upload to S3 (optional)
aws s3 cp backup-*.sql s3://your-backup-bucket/kairos/

# Keep only last 7 days of backups
find . -name "backup-*.sql" -mtime +7 -delete
```

### Automated Backup (Cron)

```bash
# Add to crontab
0 2 * * * /path/to/scripts/backup.sh
```

## 📞 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connectivity
pg_isready -h localhost -p 5432

# Check logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Memory Issues
```bash
# Check resource usage
docker stats

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
```

#### SSL Certificate Issues
```bash
# Check certificate expiry
openssl x509 -in certificate.crt -text -dates

# Renew Let's Encrypt certificate
certbot renew --nginx
```

### Performance Tuning

#### Database Optimization
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM events WHERE user_id = 1;

-- Create indexes
CREATE INDEX CONCURRENTLY idx_events_user_start ON events(user_id, start_time);

-- Update statistics
ANALYZE events;
```

#### Application Performance
```python
# Enable query logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Add caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

FastAPICache.init(RedisBackend(), prefix="kairos-cache")
```

---

This deployment guide covers the major deployment scenarios. Choose the option that best fits your needs and infrastructure requirements.
