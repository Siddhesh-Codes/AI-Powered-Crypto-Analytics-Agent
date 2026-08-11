import sqlite3
import os

# Check if database file exists
db_path = 'crypto_analytics.db'
if os.path.exists(db_path):
    print(f"✅ Database file exists: {db_path}")
    
    # Connect and check contents
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check users table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("✅ Users table exists")
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"📊 Number of users: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, name, username, email, created_at FROM users")
            users = cursor.fetchall()
            print("\n👥 Users in database:")
            for user in users:
                print(f"  ID: {user[0]}, Name: {user[1]}, Username: {user[2]}, Email: {user[3]}, Created: {user[4]}")
    else:
        print("❌ Users table does not exist")
    
    conn.close()
else:
    print(f"❌ Database file not found: {db_path}")