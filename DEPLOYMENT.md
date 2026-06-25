# MediKal Backend - Deployment Guide

## Overview
This document provides step-by-step instructions to deploy the MediKal backend using Docker.

**Tech Stack:**
- Django 5.0+ with DRF
- PostgreSQL 15
- Gunicorn (WSGI server)
- Docker & Docker Compose

---

## Prerequisites

Before deployment, ensure you have:
- Docker and Docker Compose installed
- Git (for version control)
- Access to your hosting platform
- A valid domain name (optional but recommended)

### Installation Links
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/install/)

---

## Deployment Methods

### Method 1: Local Development with Docker Compose

**Best for:** Testing deployment locally before pushing to production

```bash
# Navigate to backend directory
cd backend

# Build Docker images
docker-compose build

# Start containers
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop containers
docker-compose down
```

**Access:** http://localhost:8000

---

### Method 2: Linux Server Deployment

**Best for:** Self-hosted servers (VPS, dedicated servers)

#### Step 1: Prepare Server
```bash
# SSH into your server
ssh user@your-server-ip

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Step 2: Clone or Upload Project
```bash
# Clone from Git (if using version control)
git clone <your-repo-url>
cd medikal_backend/backend

# OR upload your project files
scp -r /path/to/backend user@your-server-ip:/home/user/medikal_backend
```

#### Step 3: Configure Production Environment
```bash
# Create/edit .env.production with:
# - Real SECRET_KEY (already generated)
# - Real ALLOWED_HOSTS (your domain)
# - Strong DB_PASSWORD
# - SSL settings

nano .env.production
```

#### Step 4: Start Services
```bash
# Pull images and start containers
docker-compose -f docker-compose.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

---

### Method 3: Cloud Deployment (AWS, GCP, Azure, Heroku, Railway)

#### Option A: Heroku / Railway (Easiest)

**Railway Deployment:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Configure environment variables
railway variables set SECRET_KEY=your-secret-key
railway variables set DEBUG=False
railway variables set ALLOWED_HOSTS=your-domain.com

# Deploy
railway up
```

**Heroku Deployment:**
```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:standard-0

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com

# Deploy
git push heroku main
```

#### Option B: AWS ECS (Container Service)
```bash
# Push image to ECR (Elastic Container Registry)
aws ecr create-repository --repository-name medikal-backend

# Tag and push image
docker tag medikal-backend:latest <aws-account-id>.dkr.ecr.<region>.amazonaws.com/medikal-backend:latest
docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/medikal-backend:latest

# Create ECS cluster and task definition
# (Use AWS Console or AWS CLI)
```

---

## Post-Deployment Checklist

- [ ] Update `ALLOWED_HOSTS` in `.env.production`
- [ ] Set a strong `SECRET_KEY`
- [ ] Change default database password
- [ ] Enable SSL/TLS (HTTPS)
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring/alerting
- [ ] Test all API endpoints
- [ ] Verify static files are served correctly
- [ ] Test file uploads (media folder)
- [ ] Set up CI/CD pipeline
- [ ] Create admin user: `docker-compose exec web python manage.py createsuperuser`

---

## Database Management

### Create Superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

### Run Migrations
```bash
docker-compose exec web python manage.py migrate
```

### Backup Database
```bash
docker-compose exec db pg_dump -U medikal_user medikal > backup.sql
```

### Restore Database
```bash
docker-compose exec -T db psql -U medikal_user medikal < backup.sql
```

---

## Monitoring & Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
```

### Health Check
```bash
curl http://your-domain.com/api/health/
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs web

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Error
```bash
# Check DB container
docker-compose logs db

# Verify DB is running
docker-compose ps

# Check environment variables
docker-compose config
```

### Static Files Not Loading
```bash
# Recollect static files
docker-compose exec web python manage.py collectstatic --noinput
```

---

## Security Hardening

1. **Use HTTPS**
   - Install SSL certificate (Let's Encrypt recommended)
   - Update `SECURE_SSL_REDIRECT=True` in `.env.production`

2. **Environment Variables**
   - Never commit `.env.production` to version control
   - Use `.gitignore` to exclude it
   - Store secrets in secure vaults

3. **Database**
   - Use strong passwords
   - Enable database encryption
   - Regular backups

4. **CORS Settings**
   - Configure CORS headers properly in Django settings
   - Only allow trusted frontend origins

---

## Rollback / Update Process

```bash
# Stop current deployment
docker-compose down

# Pull latest code
git pull origin main

# Rebuild images
docker-compose build

# Start new deployment
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f web
```

---

## Performance Optimization

### Django Settings
- Use `ALLOWED_HOSTS` whitelist
- Enable `DEBUG=False` in production
- Use `STATIC_ROOT` and `MEDIA_ROOT`
- Configure proper caching headers

### Gunicorn Workers
Current: 3 workers
Calculation: `(2 × CPU cores) + 1`
Example: 4-core server = 9 workers

Edit `entrypoint.sh`:
```bash
exec gunicorn medikal_backend.wsgi:application --bind 0.0.0.0:8000 --workers 9
```

### Database Indexing
Create indexes on frequently queried fields to improve performance.

---

## Monitoring & Alerts

### Recommended Tools
- **Sentry** - Error tracking
- **New Relic** - Performance monitoring
- **UptimeRobot** - Uptime monitoring
- **DataDog** - Infrastructure monitoring

---

## Support & Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Django REST Framework](https://www.django-rest-framework.org/)

---

**Last Updated:** 2026-06-07
**Status:** Ready for Deployment
