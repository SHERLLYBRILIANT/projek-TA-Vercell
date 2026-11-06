#!/bin/bash

echo "🚀 Starting Gizi Balita Docker Setup..."
echo ""

# Check if docker and docker-compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker and Docker Compose found"
echo ""

# Build and start containers
echo "📦 Building and starting containers..."
docker-compose up -d

# Wait for MySQL to be ready
echo "⏳ Waiting for MySQL to be ready..."
sleep 10

# Initialize database
echo "🗄️  Initializing database..."
docker-compose exec -T flask_app python setup_db.py

# Check if initialization was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup completed successfully!"
    echo ""
    echo "📝 URLs to access:"
    echo "   - Flask App: http://localhost:5000"
    echo "   - phpMyAdmin: http://localhost:8080"
    echo ""
    echo "🔐 MySQL Credentials:"
    echo "   - Host: localhost"
    echo "   - User: root"
    echo "   - Password: root"
    echo ""
    echo "💡 Useful commands:"
    echo "   - View logs:      docker-compose logs -f"
    echo "   - Stop services:  docker-compose down"
    echo "   - Stop & remove volumes: docker-compose down -v"
else
    echo "❌ Database initialization failed"
    exit 1
fi
