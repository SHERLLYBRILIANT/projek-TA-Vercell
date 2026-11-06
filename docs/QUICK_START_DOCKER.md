## Gizi Balita - Docker Quick Start

### Prerequisites
- Docker Desktop installed ([Get Docker](https://www.docker.com/products/docker-desktop))
- Windows PowerShell atau Command Prompt

### Quick Start untuk Windows

#### Option 1: Automated Setup (Recommended)
```powershell
# Run the setup script
.\docker-setup.ps1
```

#### Option 2: Manual Setup
```powershell
# 1. Start all services
docker-compose up -d

# 2. Wait 15 seconds for MySQL to be ready
Start-Sleep -Seconds 15

# 3. Initialize database
docker-compose exec flask_app python setup_db.py

# 4. Access the app
# - Flask: http://localhost:5000 (admin/admin123)
# - phpMyAdmin: http://localhost:8080 (root/root)
```

### Docker Commands

```powershell
# View logs
docker-compose logs -f

# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Remove everything
docker-compose down -v

# Execute command in container
docker-compose exec flask_app python <script_name>
```

### Services

| Service | URL | User | Password |
|---------|-----|------|----------|
| Flask App | http://localhost:5000 | admin | admin123 |
| phpMyAdmin | http://localhost:8080 | root | root |
| MySQL | localhost:3306 | root | root |

### Troubleshooting

**Port already in use?**
```powershell
# Change port in docker-compose.yml
# ports:
#   - "5001:5000"  # Change 5000 to available port
```

**MySQL connection error?**
```powershell
# Check logs
docker-compose logs mysql

# Restart MySQL
docker-compose restart mysql

# Wait and retry setup
docker-compose exec flask_app python setup_db.py
```

**Want to stop everything?**
```powershell
docker-compose down
```

**Want to start fresh?**
```powershell
docker-compose down -v  # Remove volumes too
docker-compose up -d
docker-compose exec flask_app python setup_db.py
```

---

📖 For detailed documentation, see [DOCKER_SETUP.md](DOCKER_SETUP.md)
