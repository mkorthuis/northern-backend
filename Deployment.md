# NH Facts - Heroku Deployment Guide

## 1. Initial Setup
```bash
# Install Heroku CLI if not already installed
brew install heroku/brew/heroku

# Login to Heroku
heroku login

# Create new Heroku app
heroku create nh-facts

# Set stack to container
heroku stack:set container
```

## 2. Database Setup
```bash
# Create PostgreSQL addon
heroku addons:create heroku-postgresql:essential-1

# Wait for database to be ready
heroku pg:wait

# Verify database provisioning
heroku pg:info
```

## 3. Environment Configuration
```bash
# Project settings
heroku config:set PROJECT_NAME="NH Facts"
heroku config:set STACK_NAME=nh-facts-ai
heroku config:set FRONTEND_HOST=https://nh-facts.michaelkorthuis.com
heroku config:set BACKEND_CORS_ORIGINS="http://localhost,http://localhost:5174,https://localhost,https://localhost:5174,https://nh-facts.michaelkorthuis.com,https://www.nh-facts.com"
heroku config:set SECRET_KEY=updatethis

# Get DATABASE_URL parts and set database configuration
db_host=$(heroku config:get DATABASE_URL | sed 's/.*@\([^:]*\).*/\1/')
db_port=$(heroku config:get DATABASE_URL | sed 's/.*:\([0-9]*\)\/.*/\1/')
db_name=$(heroku config:get DATABASE_URL | sed 's/.*\/\(.*\)/\1/')
db_user=$(heroku config:get DATABASE_URL | sed 's/.*:\/\/\([^:]*\):.*/\1/')
db_password=$(heroku config:get DATABASE_URL | sed 's/.*:\/\/[^:]*:\([^@]*\).*/\1/')

# Set database environment variables
heroku config:set POSTGRES_SERVER=$db_host
heroku config:set POSTGRES_PORT=$db_port
heroku config:set POSTGRES_DB=$db_name
heroku config:set POSTGRES_USER=$db_user
heroku config:set POSTGRES_PASSWORD=$db_password

# Additional settings
heroku config:set DOCKER_IMAGE_BACKEND=nh-facts-backend
heroku config:set PYTHONPATH=/app
heroku config:set PYTHONUNBUFFERED=1

# Default LLM provider
heroku config:set DEFAULT_LLM_PROVIDER=claude

heroku config:set WEB_CONCURRENCY=4 WORKER_CLASS=uvicorn.workers.UvicornWorker TIMEOUT=120

# SMTP
heroku config:set SMTP_HOST=smtp.gmail.com
heroku config:set SMTP_PORT=587
heroku config:set SMTP_USER=me@michaelkorthuis.com
heroku config:set SMTP_PASSWORD=wcyevfbquomivgip
heroku config:set ADMIN_EMAIL=me@michaelkorthuis.com

# Verify configuration
heroku config
```

## 4. Deployment
```bash
# Deploy to Heroku
git push heroku master  # or main depending on your branch name
```

## 5. Post-Deployment
```bash
# Check the application status
heroku ps

# View logs
heroku logs --tail
```

## 6. Monitoring and Management

### Check Application Status
```bash
# View process status
heroku ps

# Check logs
heroku logs --tail

# View application info
heroku apps:info
```

### Database Management
```bash
# Check database status
heroku pg:info

# Connect to database
heroku pg:psql

# Monitor database metrics
heroku pg:diagnose

#Connecting locally to the database
# Displays maintenance database,host, port, user, and password
heroku pg:credentials:url DATABASE -a nh-facts

```

### Scaling
```bash
# Scale web dynos
heroku ps:scale web=1

# View current scale
heroku ps
```

## 7. Important Notes

1. **Process Management**:
   - The application runs using the start.sh script
   - Uvicorn runs with 4 workers
   - The PORT is automatically set by Heroku

2. **Database**:
   - Using Heroku Postgres essential-1 tier
   - Database credentials are automatically managed through DATABASE_URL
   - Connection parameters are parsed from DATABASE_URL
   - Automatic backups are included with essential-1 tier

3. **Monitoring**:
   - Use `heroku logs --tail` for real-time logs
   - Check `heroku ps` for process status
   - Monitor database with `heroku pg:info`

4. **Troubleshooting**:
   - Check logs for startup issues
   - Verify environment variables with `heroku config`
   - Ensure database migrations are complete
   - Monitor process status for crashes

## 8. Useful Commands

### Quick Reference
```bash
# View logs
heroku logs --tail

# Check process status
heroku ps

# Restart application
heroku restart

# Check configuration
heroku config

# Connect to running dyno
heroku run bash

# Check database status
heroku pg:info

# View database credentials
heroku config:get DATABASE_URL

# Check database connection
heroku pg:psql
```