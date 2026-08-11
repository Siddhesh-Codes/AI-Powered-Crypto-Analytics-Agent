"""
Fix database schema by adding missing columns
"""

import sqlite3
import os

DATABASE_PATH = 'crypto_analytics.db'

def fix_database():
    """Add missing columns to existing database"""
    print("🔧 Fixing database schema...")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Check if last_login column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'last_login' not in columns:
            print("Adding 'last_login' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL")
            conn.commit()
            print("✅ Added 'last_login' column successfully!")
        else:
            print("✅ 'last_login' column already exists")
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"\n📊 Current users table columns: {', '.join(columns)}")
        
        conn.close()
        print("\n✅ Database schema fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    if os.path.exists(DATABASE_PATH):
        fix_database()
    else:
        print(f"❌ Database file '{DATABASE_PATH}' not found!")
        print("Please make sure you're running this from the backend directory.")
