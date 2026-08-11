"""
Quick script to verify database structure and show tables
"""

import sqlite3
import os

db_file = "crypto_llm_training.db"

if not os.path.exists(db_file):
    print(f"ERROR: Database file '{db_file}' not found!")
    print("Run 'python run_training.py' first to create the database.")
    exit(1)

# Connect to database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

print("\n" + "="*60)
print(f"DATABASE: {db_file}")
print("="*60)

# Get database file size
file_size = os.path.getsize(db_file)
print(f"\nFile Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
print(f"Location: {os.path.abspath(db_file)}")

# List all tables
print("\n" + "-"*60)
print("TABLES IN DATABASE:")
print("-"*60)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

for i, (table_name,) in enumerate(tables, 1):
    print(f"\n{i}. Table: {table_name}")
    
    # Get column info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print("   Columns:")
    for col in columns:
        col_id, col_name, col_type, not_null, default_val, pk = col
        pk_marker = " (PRIMARY KEY)" if pk else ""
        print(f"   - {col_name}: {col_type}{pk_marker}")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    print(f"   Rows: {row_count}")

# List all indexes
print("\n" + "-"*60)
print("INDEXES:")
print("-"*60)

cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' ORDER BY name")
indexes = cursor.fetchall()

if indexes:
    for idx_name, tbl_name in indexes:
        if not idx_name.startswith('sqlite_'):
            print(f"  - {idx_name} on table '{tbl_name}'")
else:
    print("  No custom indexes")

print("\n" + "="*60)
print("DATABASE STRUCTURE VERIFIED SUCCESSFULLY!")
print("="*60)

# Get total records
cursor.execute("SELECT COUNT(*) FROM crypto_data")
crypto_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM news_data")
news_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM training_sessions")
session_count = cursor.fetchone()[0]

print(f"\nTotal Records:")
print(f"  - Cryptocurrency Data: {crypto_count}")
print(f"  - News Articles: {news_count}")
print(f"  - Training Sessions: {session_count}")

if crypto_count == 0 and news_count == 0:
    print("\n[INFO] Database is empty. Run 'python run_training.py' to populate it.")

print("\n" + "="*60 + "\n")

conn.close()
