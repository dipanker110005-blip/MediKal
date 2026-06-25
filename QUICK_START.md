# MediKal Backend - Quick Deployment Guide

## ✨ Your Project is Ready to Deploy!

### Current Setup
- ✅ Docker configured (Dockerfile ready)
- ✅ Docker Compose configured (multi-service setup)
- ✅ Django settings configured for environment variables
- ✅ PostgreSQL container ready
- ✅ Gunicorn server configured
- ✅ Static & media file handling ready
- ✅ JWT authentication enabled

---

## 🚀 Quick Start (Local Testing)

### 1. Build & Start Services
```bash
cd backend
docker-compose build
docker-compose up -d
```

### 2. Create Admin User
```bash
docker-compose exec web python manage.py createsuperuser
```

### 3. Access Your App
- **Backend API:** http://localhost:8000/api/
- **Admin Panel:** http://localhost:8000/admin/
- **API Docs:** http://localhost:8000/swagger/ (if configured)

### 4. Stop Services
```bash
docker-compose down
```

---

## 🌍 Production Deployment

### Step 1: Update Configuration
```bash
# Edit .env.production
nano backend/.env.production

# Update these values:
# - ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
# - DB_PASSWORD=your-secure-password
# - (SECRET_KEY already updated)
```

### Step 2: Choose Deployment Platform

#### Option A: Self-Hosted Server (Linux VPS)
```bash
# SSH into server and run:
git clone your-repo-url
cd medikal_backend/backend

# Setup Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Deploy
docker-compose -f docker-compose.yml up -d
```

#### Option B: Heroku (Easiest)
```bash
heroku login
heroku create your-app-name
heroku addons:create heroku-postgresql:standard-0
git push heroku main
```

#### Option C: Railway (Recommended)
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### Step 3: Setup SSL/HTTPS
```bash
# For self-hosted with Let's Encrypt:
sudo apt-get install certbot
sudo certbot certonly --standalone -d yourdomain.com
```

---

## 🛠️ Common Commands

### Logs
```bash
docker-compose logs -f web        # Django logs
docker-compose logs -f db         # Database logs
docker-compose logs               # All logs
```

### Database
```bash
# Migrations
docker-compose exec web python manage.py migrate

# Create backup
docker-compose exec db pg_dump -U medikal_user medikal > backup.sql

# Restore backup
docker-compose exec -T db psql -U medikal_user medikal < backup.sql
```

### Maintenance
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Shell access
docker-compose exec web python manage.py shell

# Database reset (⚠️ Deletes all data!)
docker-compose exec web python manage.py flush
```

---

## ⚠️ Important Security Steps

### Before Going to Production
- [ ] Change `DEBUG=False` in `.env.production`
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Set a strong `DB_PASSWORD`
- [ ] Install SSL certificate
- [ ] Update `CORS_ALLOWED_ORIGINS` in Django settings
- [ ] Change default `SECRET_KEY` (already done ✓)
- [ ] Set `SECURE_SSL_REDIRECT=True`
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Set `CSRF_COOKIE_SECURE=True`

### Environment Variables to Customize
```
SECRET_KEY=jU5Urj=U(S)AZB/\9)'eCk.<5Q&gx;D\$E#L_ECDZ%T`jB:vsA
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=your-secure-password-here
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 📊 Performance Tips

### Database Optimization
- Add indexes to frequently queried fields
- Use database query caching
- Monitor slow queries

### Application Optimization
- Increase Gunicorn workers (current: 3)
- Enable static file caching headers
- Use CDN for media/static files
- Enable gzip compression

### Increase Gunicorn Workers
Edit `entrypoint.sh`:
```bash
# Current formula: (2 × CPU cores) + 1
# For 4-core server:
exec gunicorn medikal_backend.wsgi:application --bind 0.0.0.0:8000 --workers 9
```

---

## 🔍 Monitoring & Health Checks

### Check Container Status
```bash
docker-compose ps
```

### Health Check Endpoint
```bash
curl http://localhost:8000/api/health/
```

### Monitor Logs in Real-time
```bash
docker-compose logs -f --tail=50 web
```

---

## 🆘 Troubleshooting

### App won't start?
```bash
docker-compose logs web    # Check error message
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Can't connect to database?
```bash
docker-compose ps           # Check if db container is running
docker-compose logs db      # Check database logs
# Restart database
docker-compose restart db
```

### Static files not loading?
```bash
docker-compose exec web python manage.py collectstatic --noinput
docker-compose restart web
```

### Migrations failing?
```bash
docker-compose exec web python manage.py migrate --noinput
docker-compose exec web python manage.py migrate --noinput --fake-initial
```

---

## 📚 Resources

- [Full Deployment Guide](../DEPLOYMENT.md)
- [Docker Docs](https://docs.docker.com/)
- [Django Deployment Guide](https://docs.djangoproject.com/en/5.0/howto/deployment/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## ✅ Next Steps

1. **Test Locally First**
   ```bash
   cd backend
   docker-compose up -d
   ```

2. **Create Superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

3. **Test API Endpoints**
   - Visit http://localhost:8000/api/
   - Login at http://localhost:8000/admin/

4. **Push to Production**
   - Update `.env.production` with real values
   - Choose deployment platform
   - Follow deployment instructions in `DEPLOYMENT.md`

5. **Monitor in Production**
   - Set up logging
   - Configure monitoring tools
   - Setup database backups

---

**Ready to deploy? Start with local testing first!** 🚀

