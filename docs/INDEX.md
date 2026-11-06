# 📚 Gizi Balita - Docker Documentation Index

Dokumentasi lengkap untuk aplikasi Gizi Balita yang telah dimigrasi ke Docker.

---

## 🚀 Getting Started (Recommended Path)

1. **First Time Setup?** → [QUICK_START_DOCKER.md](QUICK_START_DOCKER.md)
2. **Need Detailed Guide?** → [DOCKER_SETUP.md](DOCKER_SETUP.md)
3. **Having Issues?** → [TROUBLESHOOTING_DATABASE.md](TROUBLESHOOTING_DATABASE.md)

---

## 📖 Documentation Structure

### Quick References
- 🏃 [QUICK_START_DOCKER.md](QUICK_START_DOCKER.md) - Fast setup untuk Windows (5 mins)
- 📋 [DOCKER_COMMANDS.md](DOCKER_COMMANDS.md) - Common Docker commands reference
- 🔗 [.env.example](.env.example) - Environment variables template

### Comprehensive Guides
- 📖 [DOCKER_SETUP.md](DOCKER_SETUP.md) - Complete Docker setup guide (semua OS)
- 🔧 [TROUBLESHOOTING_DATABASE.md](TROUBLESHOOTING_DATABASE.md) - Database issues & solutions
- 🔄 [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) - XAMPP → Docker migration details

### Configuration Files
- 🐳 [docker-compose.yml](docker-compose.yml) - Service definitions
- 📦 [Dockerfile](Dockerfile) - Flask app build configuration
- 🔑 [.env](.env) - Environment variables (auto-generated)
- 🔑 [.env.example](.env.example) - Template for .env

### Utility Scripts
- 🛠️ [setup_db.py](setup_db.py) - Database initialization (updated for Docker)
- 🧪 [test_db_connection.py](test_db_connection.py) - Connection diagnostics
- 🐚 [docker-setup.ps1](docker-setup.ps1) - Windows automated setup
- 🐚 [docker-setup.sh](docker-setup.sh) - Linux/Mac automated setup
- 🔌 [docker-entrypoint.sh](docker-entrypoint.sh) - Container startup script

---

## ⚡ Quick Commands

### Setup & Run
```powershell
# Option 1: Automated (Recommended)
.\docker-setup.ps1

# Option 2: Manual
docker-compose up -d
Start-Sleep -Seconds 15
docker-compose exec flask_app python setup_db.py
```

### Access Application
| Service | URL | Credentials |
|---------|-----|-------------|
| Flask App | http://localhost:5000 | admin / admin123 |
| phpMyAdmin | http://localhost:8080 | root / root |
| MySQL | localhost:3306 | root / root |

### Monitoring
```powershell
docker-compose ps           # Check status
docker-compose logs -f      # View logs
docker-compose exec flask_app python test_db_connection.py  # Test connection
```

### Cleanup
```powershell
docker-compose stop         # Stop services
docker-compose down         # Remove containers
docker-compose down -v      # Remove everything including volumes
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│        Docker Compose Network           │
│         (gizi_network)                  │
├─────────────────────────────────────────┤
│                                         │
│  MySQL 8.0        Flask App    phpMyAdmin│
│  Port 3306   →  Port 5000  →  Port 8080│
│  (database)    (application)  (admin)   │
│                                         │
└─────────────────────────────────────────┘
```

### Services Detail

| Service | Image | Port | Host | Status |
|---------|-------|------|------|--------|
| **mysql** | mysql:8.0 | 3306 | mysql | ✅ Production-ready |
| **flask_app** | python:3.11-slim | 5000 | localhost | ✅ Auto-init |
| **phpmyadmin** | phpmyadmin:latest | 8080 | localhost | ✅ Optional |

---

## 🔍 Troubleshooting Quick Links

### Common Issues

- **"Can't connect to MySQL server"**
  → [Database Connection Issues](TROUBLESHOOTING_DATABASE.md#error-1-cant-connect-to-mysql-server)

- **"Access denied for user"**
  → [Access Denied](TROUBLESHOOTING_DATABASE.md#error-2-access-denied-for-user)

- **"Port already in use"**
  → [Port Already in Use](TROUBLESHOOTING_DATABASE.md#error-4-port-already-in-use)

- **"Unknown database"**
  → [Unknown Database](TROUBLESHOOTING_DATABASE.md#error-3-unknown-database-gizi_balita)

📍 Lihat [TROUBLESHOOTING_DATABASE.md](TROUBLESHOOTING_DATABASE.md) untuk masalah lainnya

---

## 📊 Configuration at a Glance

### Environment Variables
```env
FLASK_ENV=development
MYSQL_HOST=mysql              # Important: 'mysql' for Docker, 'localhost' for local
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DB=gizi_balita
SECRET_KEY=gizi-balita-secret-key-2024
```

### Docker Network
- Type: Bridge
- Name: `gizi_network`
- Services can communicate via service name (e.g., `mysql://root:root@mysql:3306`)

### Volumes
- MySQL data: `mysql_data` (persistent storage)
- Flask app: `.` (volume mount for development)

---

## 🔐 Important Notes

### ⚠️ Development vs Production

**Development (Current)**
- MySQL password: `root`
- Secret key: Standard
- Debug mode: Enabled
- Suitable for: Local development only

**Production** (Sebelum deploy)
- [ ] Change MySQL password
- [ ] Generate strong secret key
- [ ] Set FLASK_ENV=production
- [ ] Use environment secrets management
- [ ] Configure proper backups
- [ ] Set up monitoring & logging

Lihat [DOCKER_SETUP.md - Security Section](DOCKER_SETUP.md#-security-notes) untuk details.

---

## 📝 First Time Setup Checklist

- [ ] Docker Desktop installed & running
- [ ] Run setup script: `.\docker-setup.ps1`
- [ ] Wait for MySQL to be ready (15 seconds)
- [ ] Database initialization completes
- [ ] Access Flask app: http://localhost:5000
- [ ] Login with admin/admin123
- [ ] Test database: `docker-compose exec flask_app python test_db_connection.py`

---

## 🎯 Common Tasks

### Restart Everything
```powershell
docker-compose restart
```

### Check Status
```powershell
docker-compose ps
```

### View Recent Logs
```powershell
docker-compose logs --tail=50
```

### Run Python Script in Container
```powershell
docker-compose exec flask_app python <script_name>
```

### Access Database
```powershell
# Via phpMyAdmin
# http://localhost:8080

# Via MySQL CLI
docker-compose exec mysql mysql -u root -proot gizi_balita
```

### Backup Database
```powershell
docker-compose exec mysql mysqldump -u root -proot gizi_balita > backup.sql
```

📍 More commands: [DOCKER_COMMANDS.md](DOCKER_COMMANDS.md)

---

## 📞 Getting Help

### Before Asking for Help, Gather:

1. **Status Check**
   ```powershell
   docker-compose ps
   ```

2. **Logs** (last 50 lines)
   ```powershell
   docker-compose logs --tail=50
   ```

3. **Connection Test**
   ```powershell
   docker-compose exec flask_app python test_db_connection.py
   ```

4. **Specific Error Message**

---

## 📚 Related Documentation

### External References
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [MySQL Docker Hub](https://hub.docker.com/_/mysql)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-MySQLdb](https://flask-mysqldb.readthedocs.io/)

### Project Documentation
- [README.md](README.md) - Project overview
- [SETUP_INFORMASI_MODEL.md](SETUP_INFORMASI_MODEL.md) - Model information
- [PERBAIKAN_MODEL_INFO.md](PERBAIKAN_MODEL_INFO.md) - Model improvements

---

## 🔄 File Structure

```
gizi_balita/
├── 📚 Documentation (NEW)
│   ├── DOCKER_SETUP.md                 # Comprehensive guide
│   ├── QUICK_START_DOCKER.md           # Quick reference
│   ├── DOCKER_COMMANDS.md              # Command reference
│   ├── TROUBLESHOOTING_DATABASE.md     # Troubleshooting
│   ├── MIGRATION_SUMMARY.md            # Migration details
│   └── INDEX.md                         # This file
│
├── 🐳 Docker Configuration (NEW)
│   ├── docker-compose.yml              # Services definition
│   ├── Dockerfile                      # Flask app build
│   ├── docker-entrypoint.sh            # Startup script
│   ├── .env                            # Environment variables
│   ├── .env.example                    # Template
│   ├── .dockerignore                   # Build optimization
│   └── .gitignore                      # Git ignore patterns
│
├── 🛠️ Utility Scripts (UPDATED)
│   ├── setup_db.py                     # Modified for Docker
│   ├── test_db_connection.py           # New: Connection test
│   ├── docker-setup.ps1                # New: Windows setup
│   └── docker-setup.sh                 # New: Linux/Mac setup
│
├── 📦 Application Files
│   ├── app.py                          # Main Flask app (no change needed)
│   ├── requirements.txt                # Dependencies (no change)
│   ├── models/                         # ML models
│   ├── static/                         # CSS, JS, uploads
│   ├── templates/                      # HTML templates
│   └── utils/                          # Utility modules
│
└── 📄 Other
    ├── database.sql                    # Database schema
    ├── README.md                       # Original README
    └── ...
```

---

## ✅ Verification

Setelah setup selesai, pastikan:

```powershell
# 1. All containers running
docker-compose ps
# Output: 3 containers with status "Up"

# 2. MySQL is healthy
# Output: mysql service should have "(healthy)" status

# 3. Connection test passes
docker-compose exec flask_app python test_db_connection.py
# Output: "✅ All tests passed!"

# 4. App is accessible
# Browser: http://localhost:5000
# Can login with admin/admin123

# 5. phpMyAdmin accessible
# Browser: http://localhost:8080
# Login: root/root
```

---

## 🎓 Learning Path

### Beginner
1. [QUICK_START_DOCKER.md](QUICK_START_DOCKER.md) - Just run it
2. Access app at http://localhost:5000

### Intermediate
1. [DOCKER_SETUP.md](DOCKER_SETUP.md) - Understand the setup
2. [DOCKER_COMMANDS.md](DOCKER_COMMANDS.md) - Learn common commands
3. Experiment with docker-compose commands

### Advanced
1. [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) - Understand architecture
2. [TROUBLESHOOTING_DATABASE.md](TROUBLESHOOTING_DATABASE.md) - Deep dive
3. Modify docker-compose.yml for custom needs

---

## 📞 Support

### Immediate Issue?
1. Check [TROUBLESHOOTING_DATABASE.md](TROUBLESHOOTING_DATABASE.md)
2. Run `docker-compose exec flask_app python test_db_connection.py`
3. Check logs: `docker-compose logs -f`

### Still Stuck?
- Provide output from above commands
- Show error messages exactly as they appear
- Describe what you've already tried

---

## 🎉 Ready to Go!

Everything is configured. You can now:

1. **Start services**
   ```powershell
   .\docker-setup.ps1  # Automated
   # or
   docker-compose up -d  # Manual
   ```

2. **Access application**
   - Flask: http://localhost:5000
   - phpMyAdmin: http://localhost:8080

3. **Login with default credentials**
   - Username: `admin`
   - Password: `admin123`

---

**Last Updated**: May 2026
**Version**: Docker 24.0+, Docker Compose 2.0+
**Status**: ✅ Ready for Development & Production
