#!/usr/bin/env python3
"""
Database Schema Migration Script
Adds missing last_login column to users table
"""

import sqlite3
import sys
from datetime import datetime

def migrate_database():
    """Add missing last_login column to users table"""
    try:
        # Connect to database
        conn = sqlite3.connect('crypto_analytics.db')
        cursor = conn.cursor()
        
        print("🔧 Starting database migration...")
        
        # Check if last_login column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📊 Current columns: {columns}")
        
        if 'last_login' not in columns:
            print("➕ Adding last_login column...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN last_login TIMESTAMP DEFAULT NULL
            """)
            print("✅ Added last_login column successfully!")
        else:
            print("✅ last_login column already exists!")
        
        # Check if we need to update existing users
        cursor.execute("SELECT COUNT(*) FROM users WHERE last_login IS NULL")
        null_count = cursor.fetchone()[0]
        
        if null_count > 0:
            print(f"🔄 Updating {null_count} users with NULL last_login...")
            current_time = datetime.now().isoformat()
            cursor.execute("""
                UPDATE users 
                SET last_login = ? 
                WHERE last_login IS NULL
            """, (current_time,))
            print("✅ Updated existing users!")
        
        # Verify the schema
        cursor.execute("PRAGMA table_info(users)")
        columns_after = cursor.fetchall()
        print("\n📋 Final table schema:")
        for column in columns_after:
            print(f"  - {column[1]} ({column[2]}) {'NOT NULL' if column[3] else 'NULL'}")
        
        # Check some sample data
        cursor.execute("SELECT id, name, username, email, last_login FROM users LIMIT 3")
        users = cursor.fetchall()
        print(f"\n👥 Sample user data ({len(users)} users):")
        for user in users:
            print(f"  - ID: {user[0]}, Name: {user[1]}, Username: {user[2]}, Email: {user[3]}, Last Login: {user[4]}")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Database migration completed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)