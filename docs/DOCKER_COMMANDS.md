# 🐳 Docker Commands Reference

Quick reference untuk Docker commands yang sering digunakan.

## 🚀 Getting Started

### Start All Services
```powershell
docker-compose up -d
```

### Stop All Services
```powershell
docker-compose stop
```

### Stop and Remove Containers
```powershell
docker-compose down
```

### Stop and Remove Everything (including volumes)
```powershell
docker-compose down -v
```

---

## 🔍 Monitoring & Inspection

### View Status of All Containers
```powershell
docker-compose ps
```

### View Real-time Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f flask_app
docker-compose logs -f mysql
docker-compose logs -f phpmyadmin
```

### View Last N Lines of Logs
```powershell
# Last 50 lines
docker-compose logs --tail=50

# All logs of specific service
docker-compose logs flask_app --tail=100
```

### Container Resource Usage
```powershell
docker stats
```

### Detailed Container Info
```powershell
docker inspect gizi_balita_flask
docker inspect gizi_balita_mysql
docker inspect gizi_balita_phpmyadmin
```

---

## 🔄 Managing Services

### Restart All Services
```powershell
docker-compose restart
```

### Restart Specific Service
```powershell
docker-compose restart flask_app
docker-compose restart mysql
```

### Pause/Unpause Services
```powershell
docker-compose pause        # Pause all
docker-compose pause mysql  # Pause specific
docker-compose unpause      # Unpause all
```

### Rebuild Images
```powershell
# Rebuild Flask app image
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Rebuild specific service
docker-compose build flask_app
```

---

## 💻 Executing Commands

### Execute Command in Container
```powershell
# Run Python script
docker-compose exec flask_app python setup_db.py
docker-compose exec flask_app python test_db_connection.py

# Run MySQL command
docker-compose exec mysql mysql -u root -proot gizi_balita -e "SELECT COUNT(*) FROM petugas;"

# Open bash shell in container
docker-compose exec flask_app bash
docker-compose exec mysql bash

# Non-interactive execution
docker-compose exec -T flask_app python setup_db.py
```

### Run Commands in New Container
```powershell
docker-compose run flask_app python setup_db.py
```

---

## 🗄️ Database Management

### Access MySQL CLI
```powershell
docker-compose exec mysql mysql -u root -proot gizi_balita
```

### Run SQL Query
```powershell
docker-compose exec mysql mysql -u root -proot gizi_balita -e "SELECT * FROM petugas;"
```

### Backup Database
```powershell
docker-compose exec mysql mysqldump -u root -proot gizi_balita > backup.sql
```

### Restore Database
```powershell
docker-compose exec -T mysql mysql -u root -proot gizi_balita < backup.sql
```

### Check Database Size
```powershell
docker-compose exec mysql mysql -u root -proot -e "SELECT table_schema, ROUND(SUM(data_length+index_length)/1024/1024,2) as size_mb FROM information_schema.tables GROUP BY table_schema;"
```

---

## 📝 Volumes & Networks

### List Volumes
```powershell
docker volume ls
```

### Inspect Volume
```powershell
docker volume inspect gizi_balita_project_gizi_balita_mysql_data
```

### Remove Unused Volumes
```powershell
docker volume prune
```

### List Networks
```powershell
docker network ls
```

### Inspect Network
```powershell
docker network inspect gizi_network
```

---

## 🧪 Testing & Debugging

### Test Database Connection
```powershell
docker-compose exec flask_app python test_db_connection.py
```

### Ping Service from Container
```powershell
# Ping MySQL from Flask container
docker-compose exec flask_app ping mysql

# Should return: PING mysql (172.x.x.x)
```

### Test Connectivity
```powershell
# DNS resolution test
docker-compose exec flask_app nslookup mysql

# Port connectivity test
docker-compose exec flask_app nc -zv mysql 3306
```

### Access Application
```powershell
# Direct URL access
curl http://localhost:5000/login

# From within container
docker-compose exec flask_app curl http://localhost:5000/login
```

---

## 🧹 Cleanup

### Remove Stopped Containers
```powershell
docker container prune
```

### Remove Unused Images
```powershell
docker image prune
```

### Remove All Unused Docker Objects
```powershell
docker system prune
```

### Remove Everything (DANGEROUS!)
```powershell
# Remove all stopped containers
docker container prune -f

# Remove all unused images
docker image prune -af

# Remove all unused volumes
docker volume prune -f
```

---

## 🔧 Development Workflow

### Development Setup
```powershell
# 1. Start services
docker-compose up -d

# 2. Wait for MySQL
Start-Sleep -Seconds 15

# 3. Initialize database
docker-compose exec flask_app python setup_db.py

# 4. View logs
docker-compose logs -f
```

### Code Changes
```powershell
# Changes are reflected immediately (volume mounted)
# No need to restart Flask app for Python code changes

# For requirements.txt changes:
docker-compose exec flask_app pip install -r requirements.txt

# For docker-compose.yml changes:
docker-compose up -d
```

### Database Changes
```powershell
# Re-run setup script after schema changes
docker-compose exec flask_app python setup_db.py

# Or restart MySQL
docker-compose restart mysql
```

---

## 🚨 Emergency Commands

### Kill All Docker Containers
```powershell
docker kill $(docker ps -q)
```

### Remove All Docker Containers
```powershell
docker rm $(docker ps -a -q)
```

### Force Stop Service
```powershell
docker-compose kill flask_app
```

### Full Reset (Warning: Destructive!)
```powershell
# Remove everything
docker-compose down -v

# Rebuild and restart
docker-compose up -d

# Wait and setup
Start-Sleep -Seconds 20
docker-compose exec flask_app python setup_db.py
```

---

## 📚 Common Workflows

### Fresh Start
```powershell
docker-compose down -v  # Remove everything
docker-compose up -d    # Start fresh
Start-Sleep -Seconds 15
docker-compose exec flask_app python setup_db.py
```

### Quick Restart
```powershell
docker-compose restart
```

### Troubleshoot Connection
```powershell
# 1. Check status
docker-compose ps

# 2. View logs
docker-compose logs mysql

# 3. Test connection
docker-compose exec flask_app python test_db_connection.py

# 4. If needed, restart
docker-compose restart mysql
```

### Check Everything
```powershell
# Status
docker-compose ps

# Logs
docker-compose logs --tail=20

# Test connection
docker-compose exec flask_app python test_db_connection.py

# Check resources
docker stats --no-stream
```

---

## 🎯 Quick Aliases (Optional)

Add to PowerShell Profile (`$PROFILE`):

```powershell
Set-Alias dcu 'docker-compose up -d'
Set-Alias dcd 'docker-compose down'
Set-Alias dcps 'docker-compose ps'
Set-Alias dcl 'docker-compose logs -f'
Set-Alias dce 'docker-compose exec'
```

Then use:
```powershell
dcu                          # docker-compose up -d
dcps                         # docker-compose ps
dcl                          # docker-compose logs -f
dce flask_app python ...     # docker-compose exec
```

---

## 📖 Help & Documentation

```powershell
# Docker help
docker --help
docker-compose --help

# Command-specific help
docker-compose up --help
docker-compose exec --help
docker-compose logs --help
```

---

**Last Updated**: May 2026
