"""
test_db_connection.py
─────────────────────────────────────────────────────────────────────────
Script untuk mengecek koneksi ke database MySQL
Berguna untuk troubleshooting masalah koneksi database

Usage:
    python test_db_connection.py
"""

import pymysql
import os
import sys
from datetime import datetime

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_section(title):
    """Print formatted section"""
    print(f"\n📋 {title}")
    print("-"*70)

def test_connection():
    """Test database connection"""
    print_header("DATABASE CONNECTION TEST")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get configuration from environment variables
    print_section("Configuration")
    
    db_config = {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', 'root'),
        'charset': 'utf8mb4'
    }
    db_name = os.environ.get('MYSQL_DB', 'gizi_balita')
    
    print(f"  Host:     {db_config['host']}")
    print(f"  User:     {db_config['user']}")
    print(f"  Password: {'*' * len(db_config['password'])}")
    print(f"  Database: {db_name}")
    print(f"  Charset:  {db_config['charset']}")
    
    # Test basic connection
    print_section("Test 1: Basic Connection")
    try:
        conn = pymysql.connect(**db_config)
        print("  ✅ Basic connection successful")
        conn.close()
    except Exception as e:
        print(f"  ❌ Basic connection failed: {e}")
        return False
    
    # Test database selection
    print_section("Test 2: Database Selection")
    try:
        conn = pymysql.connect(database=db_name, **db_config)
        print(f"  ✅ Successfully selected database '{db_name}'")
        conn.close()
    except Exception as e:
        print(f"  ❌ Failed to select database '{db_name}': {e}")
        return False
    
    # Test table queries
    print_section("Test 3: Table Queries")
    try:
        conn = pymysql.connect(database=db_name, **db_config)
        cur = conn.cursor()
        
        # Get tables
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()
        print(f"  ✅ Found {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            print(f"     - {table_name}: {count} rows")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  ❌ Failed to query tables: {e}")
        return False
    
    # Test Flask-MySQLdb connection
    print_section("Test 4: Flask-MySQLdb Integration")
    try:
        from flask import Flask
        from flask_mysqldb import MySQL
        
        app = Flask(__name__)
        app.config['MYSQL_HOST'] = db_config['host']
        app.config['MYSQL_USER'] = db_config['user']
        app.config['MYSQL_PASSWORD'] = db_config['password']
        app.config['MYSQL_DB'] = db_name
        app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
        
        mysql = MySQL(app)
        
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("SELECT 1 AS test")
            result = cur.fetchone()
            cur.close()
            
        print("  ✅ Flask-MySQLdb connection successful")
    except Exception as e:
        print(f"  ❌ Flask-MySQLdb connection failed: {e}")
        return False
    
    # Success summary
    print_section("SUMMARY")
    print("  ✅ All tests passed!")
    print("  Database is properly configured and accessible.")
    print_header("END OF TEST")
    
    return True

if __name__ == '__main__':
    try:
        success = test_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
