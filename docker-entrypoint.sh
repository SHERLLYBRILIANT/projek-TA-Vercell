#!/bin/bash

# Docker entrypoint script
# Menjalankan setup_db jika database belum ada

set -e

echo "🚀 Flask Application Starting..."

# Function untuk check MySQL connectivity
check_mysql() {
    python -c "
import pymysql
import os
import time

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        conn = pymysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', 'root'),
            charset='utf8mb4'
        )
        print('✅ MySQL is ready!')
        conn.close()
        exit(0)
    except Exception as e:
        retry_count += 1
        if retry_count < max_retries:
            print(f'⏳ Waiting for MySQL ({retry_count}/{max_retries})...')
            time.sleep(1)
        else:
            print('❌ MySQL connection failed after retries')
            exit(1)
"
}

# Function untuk check apakah database sudah ada
check_database() {
    python -c "
import pymysql
import os

try:
    conn = pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', 'root'),
        database=os.environ.get('MYSQL_DB', 'gizi_balita'),
        charset='utf8mb4'
    )
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM petugas')
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    
    if count > 0:
        print('✅ Database sudah ada dan sudah diinisialisasi')
        exit(0)
    else:
        print('⚠️  Database ada tapi belum diinisialisasi')
        exit(1)
except Exception as e:
    print(f'⚠️  Database belum ada atau belum setup: {e}')
    exit(1)
" 2>/dev/null || return 1
}

echo "🔍 Checking MySQL connection..."
check_mysql

echo "🔍 Checking database initialization..."
if ! check_database; then
    echo "📦 Initializing database..."
    python setup_db.py
fi

echo "✅ All checks passed!"
echo "🌐 Starting Flask application..."

# Run Flask app
exec flask run --host=0.0.0.0
