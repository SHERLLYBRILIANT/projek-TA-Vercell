# docker-setup.ps1
# Docker setup script untuk Windows PowerShell

Write-Host "🚀 Starting Gizi Balita Docker Setup..." -ForegroundColor Green
Write-Host ""

# Check if docker is installed
$dockerCheck = docker --version 2>$null
if ($null -eq $dockerCheck) {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

$dockerComposeCheck = docker-compose --version 2>$null
if ($null -eq $dockerComposeCheck) {
    Write-Host "❌ Docker Compose is not installed." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker and Docker Compose found" -ForegroundColor Green
Write-Host ""

# Build and start containers
Write-Host "📦 Building and starting containers..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start containers" -ForegroundColor Red
    exit 1
}

# Wait for MySQL to be ready
Write-Host "⏳ Waiting for MySQL to be ready (15 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Initialize database
Write-Host "🗄️  Initializing database..." -ForegroundColor Yellow
docker-compose exec -T flask_app python setup_db.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 URLs to access:" -ForegroundColor Cyan
    Write-Host "   - Flask App: http://localhost:5000" -ForegroundColor White
    Write-Host "   - phpMyAdmin: http://localhost:8080" -ForegroundColor White
    Write-Host ""
    Write-Host "🔐 MySQL Credentials:" -ForegroundColor Cyan
    Write-Host "   - Host: localhost" -ForegroundColor White
    Write-Host "   - User: root" -ForegroundColor White
    Write-Host "   - Password: root" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Useful commands:" -ForegroundColor Cyan
    Write-Host "   - View logs:      docker-compose logs -f" -ForegroundColor White
    Write-Host "   - Stop services:  docker-compose down" -ForegroundColor White
    Write-Host "   - Stop & remove volumes: docker-compose down -v" -ForegroundColor White
} else {
    Write-Host "❌ Database initialization failed" -ForegroundColor Red
    exit 1
}
