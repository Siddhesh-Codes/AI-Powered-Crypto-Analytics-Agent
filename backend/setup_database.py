#!/usr/bin/env python3
"""
Database Setup Script for Crypto Analytics Authentication System
This script creates the MySQL database and tables for user authentication.
"""

import sqlite3
import os

# Database configuration - SQLite (file-based, no server needed)
DATABASE_PATH = 'crypto_analytics.db'

def create_database():
    """Create the SQLite database file"""
    try:
        # SQLite creates the database file automatically when connecting
        if not os.path.exists(DATABASE_PATH):
            connection = sqlite3.connect(DATABASE_PATH)
            connection.close()
            print(f"✅ Database '{DATABASE_PATH}' created successfully!")
        else:
            print(f"✅ Database '{DATABASE_PATH}' already exists!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_tables():
    """Create the users table and other necessary tables"""
    
    # SQL to create users table (SQLite syntax)
    users_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    """
    
    # SQL to create user sessions table (optional, for session management)
    sessions_table_sql = """
    CREATE TABLE IF NOT EXISTS user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token_hash TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """
    
    try:
        # Connect to SQLite database
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()
        
        # Create users table
        cursor.execute(users_table_sql)
        print("✅ Users table created successfully!")
        
        # Create sessions table
        cursor.execute(sessions_table_sql)
        print("✅ User sessions table created successfully!")
        
        # Create indexes for better performance
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON users(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_username ON users(username)")  
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_token_hash ON user_sessions(token_hash)")
            print("✅ Indexes created successfully!")
        except Exception as idx_error:
            print(f"⚠️ Index creation warning: {idx_error}")
            # Indexes are optional, continue anyway
        
        connection.commit()
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def test_connection():
    """Test the database connection"""
    try:
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        result = cursor.fetchone()
        print(f"✅ Database connection successful! Users table has {result[0]} records.")
        
        cursor.close()
        connection.close()
        return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Crypto Analytics Authentication Database...")
    print("=" * 60)
    
    # Step 1: Create database
    print("1️⃣ Creating database...")
    if not create_database():
        print("❌ Failed to create database. Exiting.")
        return
    
    # Step 2: Create tables
    print("\n2️⃣ Creating tables...")
    if not create_tables():
        print("❌ Failed to create tables. Exiting.")
        return
    
    # Step 3: Test connection
    print("\n3️⃣ Testing database connection...")
    if test_connection():
        print("\n🎉 Database setup completed successfully!")
        print("Your authentication system is ready to use!")
    else:
        print("\n❌ Database setup completed but connection test failed.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
