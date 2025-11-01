"""
Database Manager - Stores fetched training data in SQLite database
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

DATABASE_FILE = "crypto_llm_training.db"

class TrainingDataDB:
    """Manages the SQLite database for LLM training data"""
    
    def __init__(self, db_path=DATABASE_FILE):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.initialize_database()
    
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
    
    def initialize_database(self):
        """Create database tables if they don't exist"""
        self.connect()
        
        # Create crypto_data table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS crypto_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                volume_24h REAL,
                market_cap REAL,
                percent_change_1h REAL,
                percent_change_24h REAL,
                percent_change_7d REAL,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create news_data table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                content TEXT,
                source TEXT,
                published_at TEXT,
                url TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create training_sessions table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                model_name TEXT NOT NULL,
                num_epochs INTEGER,
                batch_size INTEGER,
                learning_rate REAL,
                total_crypto_records INTEGER,
                total_news_records INTEGER,
                final_train_loss REAL,
                final_val_loss REAL,
                final_accuracy REAL,
                training_duration REAL,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT DEFAULT 'in_progress',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_crypto_symbol 
            ON crypto_data(symbol)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_crypto_fetched 
            ON crypto_data(fetched_at)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_news_fetched 
            ON news_data(fetched_at)
        """)
        
        self.conn.commit()
        print(f"[SUCCESS] Database initialized: {self.db_path}")
    
    def insert_crypto_data(self, crypto_df):
        """Insert cryptocurrency data from DataFrame"""
        if crypto_df is None or len(crypto_df) == 0:
            return 0
        
        inserted = 0
        fetched_at = datetime.now().isoformat()
        
        for _, row in crypto_df.iterrows():
            try:
                self.cursor.execute("""
                    INSERT INTO crypto_data 
                    (symbol, name, price, volume_24h, market_cap, 
                     percent_change_1h, percent_change_24h, percent_change_7d, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row.get('symbol'),
                    row.get('name'),
                    row.get('price'),
                    row.get('volume_24h'),
                    row.get('market_cap'),
                    row.get('percent_change_1h'),
                    row.get('percent_change_24h'),
                    row.get('percent_change_7d'),
                    fetched_at
                ))
                inserted += 1
            except Exception as e:
                print(f"[ERROR] Failed to insert crypto record: {e}")
        
        self.conn.commit()
        print(f"[SUCCESS] Inserted {inserted} crypto records into database")
        return inserted
    
    def insert_news_data(self, news_df):
        """Insert news data from DataFrame"""
        if news_df is None or len(news_df) == 0:
            return 0
        
        inserted = 0
        fetched_at = datetime.now().isoformat()
        
        for _, row in news_df.iterrows():
            try:
                self.cursor.execute("""
                    INSERT INTO news_data 
                    (title, description, content, source, published_at, url, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    row.get('title'),
                    row.get('description'),
                    row.get('content'),
                    row.get('source'),
                    row.get('published_at'),
                    row.get('url'),
                    fetched_at
                ))
                inserted += 1
            except Exception as e:
                print(f"[ERROR] Failed to insert news record: {e}")
        
        self.conn.commit()
        print(f"[SUCCESS] Inserted {inserted} news records into database")
        return inserted
    
    def create_training_session(self, session_data):
        """Create a new training session record"""
        self.cursor.execute("""
            INSERT INTO training_sessions 
            (session_name, model_name, num_epochs, batch_size, learning_rate,
             total_crypto_records, total_news_records, started_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_data['session_name'],
            session_data['model_name'],
            session_data['num_epochs'],
            session_data['batch_size'],
            session_data['learning_rate'],
            session_data['total_crypto_records'],
            session_data['total_news_records'],
            datetime.now().isoformat()
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_training_session(self, session_id, results):
        """Update training session with final results"""
        self.cursor.execute("""
            UPDATE training_sessions 
            SET final_train_loss = ?,
                final_val_loss = ?,
                final_accuracy = ?,
                training_duration = ?,
                completed_at = ?,
                status = 'completed'
            WHERE id = ?
        """, (
            results['final_train_loss'],
            results['final_val_loss'],
            results['final_accuracy'],
            results['training_duration'],
            datetime.now().isoformat(),
            session_id
        ))
        self.conn.commit()
    
    def get_crypto_summary(self):
        """Get summary statistics of crypto data"""
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT symbol) as unique_symbols,
                MIN(fetched_at) as first_fetch,
                MAX(fetched_at) as last_fetch,
                AVG(price) as avg_price,
                MAX(price) as max_price,
                MIN(price) as min_price
            FROM crypto_data
        """)
        return dict(self.cursor.fetchone())
    
    def get_news_summary(self):
        """Get summary statistics of news data"""
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT source) as unique_sources,
                MIN(fetched_at) as first_fetch,
                MAX(fetched_at) as last_fetch
            FROM news_data
        """)
        return dict(self.cursor.fetchone())
    
    def get_all_crypto_data(self):
        """Get ALL cryptocurrency records for training"""
        self.cursor.execute("""
            SELECT symbol, name, price, volume_24h, market_cap,
                   percent_change_24h, fetched_at
            FROM crypto_data
            ORDER BY symbol, fetched_at
        """)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_latest_crypto_data(self, limit=10):
        """Get latest cryptocurrency records"""
        self.cursor.execute("""
            SELECT symbol, name, price, volume_24h, market_cap,
                   percent_change_24h, fetched_at
            FROM crypto_data
            ORDER BY fetched_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_latest_news_data(self, limit=10):
        """Get latest news records"""
        self.cursor.execute("""
            SELECT title, source, published_at, url, fetched_at
            FROM news_data
            ORDER BY fetched_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_all_training_sessions(self):
        """Get all training sessions"""
        self.cursor.execute("""
            SELECT * FROM training_sessions
            ORDER BY started_at DESC
        """)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def export_to_dataframe(self, table_name):
        """Export table to pandas DataFrame"""
        query = f"SELECT * FROM {table_name}"
        return pd.read_sql_query(query, self.conn)
    
    def print_database_stats(self):
        """Print comprehensive database statistics"""
        print("\n" + "="*60)
        print("DATABASE STATISTICS")
        print("="*60)
        
        # Crypto data stats
        crypto_stats = self.get_crypto_summary()
        print("\n[CRYPTOCURRENCY DATA]")
        print(f"  Total Records:     {crypto_stats['total_records']:,}")
        print(f"  Unique Symbols:    {crypto_stats['unique_symbols']}")
        if crypto_stats['total_records'] > 0:
            print(f"  Price Range:       ${crypto_stats['min_price']:,.2f} - ${crypto_stats['max_price']:,.2f}")
            print(f"  Average Price:     ${crypto_stats['avg_price']:,.2f}")
            print(f"  First Fetch:       {crypto_stats['first_fetch']}")
            print(f"  Last Fetch:        {crypto_stats['last_fetch']}")
        
        # News data stats
        news_stats = self.get_news_summary()
        print("\n[NEWS DATA]")
        print(f"  Total Records:     {news_stats['total_records']:,}")
        print(f"  Unique Sources:    {news_stats['unique_sources']}")
        if news_stats['total_records'] > 0:
            print(f"  First Fetch:       {news_stats['first_fetch']}")
            print(f"  Last Fetch:        {news_stats['last_fetch']}")
        
        # Training sessions
        sessions = self.get_all_training_sessions()
        print(f"\n[TRAINING SESSIONS]")
        print(f"  Total Sessions:    {len(sessions)}")
        
        if sessions:
            completed = [s for s in sessions if s['status'] == 'completed']
            print(f"  Completed:         {len(completed)}")
            if completed:
                latest = completed[0]
                print(f"  Latest Session:    {latest['session_name']}")
                print(f"  Final Accuracy:    {latest['final_accuracy']:.2%}")
        
        print("\n" + "="*60)
        print(f"Database Location: {os.path.abspath(self.db_path)}")
        print("="*60 + "\n")


def view_database_contents():
    """View database contents in a formatted way"""
    db = TrainingDataDB()
    
    print("\n" + "="*60)
    print("VIEWING DATABASE CONTENTS")
    print("="*60)
    
    # Show statistics
    db.print_database_stats()
    
    # Show latest crypto data
    print("\n[LATEST CRYPTOCURRENCY DATA (Top 10)]")
    print("-" * 60)
    crypto_data = db.get_latest_crypto_data(10)
    if crypto_data:
        for i, record in enumerate(crypto_data, 1):
            print(f"\n{i}. {record['name']} ({record['symbol']})")
            print(f"   Price: ${record['price']:,.2f}")
            print(f"   24h Change: {record['percent_change_24h']:.2f}%")
            print(f"   Market Cap: ${record['market_cap']:,.0f}")
            print(f"   Fetched: {record['fetched_at']}")
    else:
        print("  No data available")
    
    # Show latest news
    print("\n\n[LATEST NEWS DATA (Top 10)]")
    print("-" * 60)
    news_data = db.get_latest_news_data(10)
    if news_data:
        for i, record in enumerate(news_data, 1):
            print(f"\n{i}. {record['title']}")
            print(f"   Source: {record['source']}")
            print(f"   Published: {record['published_at']}")
            print(f"   Fetched: {record['fetched_at']}")
    else:
        print("  No data available")
    
    # Show training sessions
    print("\n\n[TRAINING SESSIONS]")
    print("-" * 60)
    sessions = db.get_all_training_sessions()
    if sessions:
        for i, session in enumerate(sessions, 1):
            print(f"\n{i}. {session['session_name']}")
            print(f"   Model: {session['model_name']}")
            print(f"   Status: {session['status']}")
            print(f"   Epochs: {session['num_epochs']}")
            print(f"   Started: {session['started_at']}")
            if session['status'] == 'completed':
                print(f"   Final Accuracy: {session['final_accuracy']:.2%}")
                print(f"   Training Loss: {session['final_train_loss']:.4f}")
                print(f"   Duration: {session['training_duration']:.2f} seconds")
    else:
        print("  No training sessions yet")
    
    print("\n" + "="*60 + "\n")
    
    db.close()


if __name__ == "__main__":
    # Initialize database
    db = TrainingDataDB()
    db.print_database_stats()
    db.close()
    
    print("\n[SUCCESS] Database system ready!")
    print(f"Database file: {os.path.abspath(DATABASE_FILE)}")
    print("\nUse 'python database_manager.py' to view database contents")
