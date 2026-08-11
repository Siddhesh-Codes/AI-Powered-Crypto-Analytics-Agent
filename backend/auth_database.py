"""
SQLite Database Configuration and User Authentication System
Created for Crypto Analytics Application
"""

import sqlite3
import bcrypt
from typing import Optional, Dict, Any
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration (SQLite)
DATABASE_PATH = 'crypto_analytics.db'

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_super_secret_jwt_key_for_crypto_app_2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

class DatabaseManager:
    """Handles SQLite database connections and operations"""
    
    def __init__(self):
        self.connection = None
        self.database_path = DATABASE_PATH
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(DATABASE_PATH)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            print("✅ Connected to SQLite database successfully!")
            return True
        except Exception as e:
            print(f"❌ Error connecting to SQLite: {e}")
            return False
        
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ SQLite connection closed.")
            
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute SQL query with error handling"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            
            if fetch:
                result = [dict(row) for row in cursor.fetchall()]
                cursor.close()
                return result
            else:
                self.connection.commit()
                cursor.close()
                return True
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None
            
    def execute_single_query(self, query: str, params: tuple = None):
        """Execute query and return single result"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return dict(result) if result else None
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None

class AuthSystem:
    """Complete authentication system with user management"""
    
    def __init__(self):
        self.db = DatabaseManager()
        
    def initialize_database(self):
        """Create database and tables if they don't exist"""
        try:
            # Connect to SQLite database
            if not self.db.connect():
                return False
                
            # Create users table
            users_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP NULL
            );
            """
            
            # Create sessions table for better security
            sessions_table_query = """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
            
            # Create indexes
            index_queries = [
                "CREATE INDEX IF NOT EXISTS idx_token_hash ON user_sessions(token_hash);",
                "CREATE INDEX IF NOT EXISTS idx_user_id ON user_sessions(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_expires_at ON user_sessions(expires_at);",
                "CREATE INDEX IF NOT EXISTS idx_username ON users(username);",
                "CREATE INDEX IF NOT EXISTS idx_email ON users(email);"
            ]
            
            # Execute table creation queries
            if self.db.execute_query(users_table_query):
                print("✅ Users table created/verified successfully!")
            else:
                print("❌ Failed to create users table")
                return False
                
            if self.db.execute_query(sessions_table_query):
                print("✅ Sessions table created/verified successfully!")
            else:
                print("❌ Failed to create sessions table")
                return False
                
            # Create indexes
            for index_query in index_queries:
                self.db.execute_query(index_query)
                
            print("✅ Database indexes created successfully!")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Error initializing database: {e}")
            return False
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt (max 72 bytes)"""
        # Bcrypt has a maximum password length of 72 bytes
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash (max 72 bytes)"""
        # Bcrypt has a maximum password length of 72 bytes
        password_bytes = password.encode('utf-8')[:72]
        return bcrypt.checkpw(password_bytes, hashed.encode('utf-8'))
    
    def generate_jwt_token(self, user_data: Dict[str, Any]) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'email': user_data['email'],
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            print("❌ Token has expired")
            return None
        except jwt.InvalidTokenError:
            print("❌ Invalid token")
            return None
    
    def register_user(self, name: str, username: str, email: str, password: str) -> Dict[str, Any]:
        """Register new user with validation"""
        
        # Validate input
        if len(password) < 6:
            return {"success": False, "message": "Password must be at least 6 characters long"}
        
        if len(username) < 3:
            return {"success": False, "message": "Username must be at least 3 characters long"}
            
        if '@' not in email:
            return {"success": False, "message": "Please enter a valid email address"}
        
        # Check if user already exists
        existing_user_query = "SELECT id FROM users WHERE username = ? OR email = ?"
        existing_user = self.db.execute_single_query(existing_user_query, (username, email))
        
        if existing_user:
            return {"success": False, "message": "Username or email already exists"}
        
        # Hash password and create user
        password_hash = self.hash_password(password)
        
        insert_query = """
        INSERT INTO users (name, username, email, password_hash) 
        VALUES (?, ?, ?, ?)
        """
        
        if self.db.execute_query(insert_query, (name, username, email, password_hash)):
            return {"success": True, "message": "Account created successfully! You can now log in."}
        else:
            return {"success": False, "message": "Failed to create account. Please try again."}
    
    def login_user(self, login_input: str, password: str) -> Dict[str, Any]:
        """Login user with username or email"""
        
        # Find user by username or email
        user_query = "SELECT * FROM users WHERE (username = ? OR email = ?) AND is_active = 1"
        user = self.db.execute_single_query(user_query, (login_input, login_input))
        
        if not user:
            return {"success": False, "message": "Invalid username/email or password"}
        
        # Verify password
        if not self.verify_password(password, user['password_hash']):
            return {"success": False, "message": "Invalid username/email or password"}
        
        # Update last login
        update_login_query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
        self.db.execute_query(update_login_query, (user['id'],))
        
        # Generate JWT token
        token = self.generate_jwt_token(user)
        
        # Store session in database
        session_query = """
        INSERT INTO user_sessions (user_id, token_hash, expires_at) 
        VALUES (?, ?, ?)
        """
        # Truncate token to 72 bytes for bcrypt (bcrypt has a 72-byte limit)
        token_bytes = token.encode('utf-8')[:72]
        token_hash = bcrypt.hashpw(token_bytes, bcrypt.gensalt()).decode('utf-8')
        expires_at = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        
        self.db.execute_query(session_query, (user['id'], token_hash, expires_at))
        
        return {
            "success": True, 
            "message": "Login successful!",
            "token": token,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "username": user['username'],
                "email": user['email']
            }
        }
    
    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from JWT token"""
        payload = self.verify_jwt_token(token)
        if not payload:
            return None
            
        user_query = "SELECT id, name, username, email FROM users WHERE id = ? AND is_active = 1"
        user = self.db.execute_single_query(user_query, (payload['user_id'],))
        
        return user
    
    def logout_user(self, token: str) -> bool:
        """Logout user by invalidating session"""
        payload = self.verify_jwt_token(token)
        if not payload:
            return False
            
        # Deactivate user sessions
        logout_query = "UPDATE user_sessions SET is_active = 0 WHERE user_id = ?"
        return self.db.execute_query(logout_query, (payload['user_id'],))
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions (run periodically)"""
        cleanup_query = "DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP OR is_active = 0"
        return self.db.execute_query(cleanup_query)
    
    def close_connection(self):
        """Close database connection"""
        self.db.disconnect()

# Initialize authentication system
auth_system = AuthSystem()

def init_auth_database():
    """Initialize the authentication database"""
    return auth_system.initialize_database()

def get_auth_system():
    """Get the authentication system instance"""
    return auth_system