"""
Test Suite 6: Auth Database Unit Tests
Tests DatabaseManager and AuthSystem classes directly
"""

import pytest
import sys
import os
import sqlite3
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_database import DatabaseManager, AuthSystem


class TestDatabaseManager:
    """Test the DatabaseManager class"""

    def test_connect_creates_db(self):
        """TC-6.1: DatabaseManager connects and creates SQLite database"""
        db = DatabaseManager()
        db.database_path = ":memory:"
        # Use in-memory db for testing
        result = db.connect()
        assert result is True
        db.disconnect()

    def test_disconnect(self):
        """TC-6.2: DatabaseManager disconnects cleanly"""
        db = DatabaseManager()
        db.database_path = ":memory:"
        db.connect()
        db.disconnect()
        # Should not raise

    def test_execute_query(self):
        """TC-6.3: Execute CREATE TABLE query"""
        db = DatabaseManager()
        db.database_path = ":memory:"
        db.connection = sqlite3.connect(":memory:")
        db.connection.row_factory = sqlite3.Row
        result = db.execute_query("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        assert result is True
        db.disconnect()

    def test_execute_query_with_params(self):
        """TC-6.4: Execute INSERT query with parameters"""
        db = DatabaseManager()
        db.connection = sqlite3.connect(":memory:")
        db.connection.row_factory = sqlite3.Row
        db.execute_query("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        result = db.execute_query("INSERT INTO test (name) VALUES (?)", ("TestName",))
        assert result is True
        db.disconnect()

    def test_execute_query_fetch(self):
        """TC-6.5: Execute SELECT query with fetch"""
        db = DatabaseManager()
        db.connection = sqlite3.connect(":memory:")
        db.connection.row_factory = sqlite3.Row
        db.execute_query("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        db.execute_query("INSERT INTO test (name) VALUES (?)", ("Alice",))
        result = db.execute_query("SELECT * FROM test", fetch=True)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "Alice"
        db.disconnect()

    def test_execute_single_query(self):
        """TC-6.6: Execute single-result query"""
        db = DatabaseManager()
        db.connection = sqlite3.connect(":memory:")
        db.connection.row_factory = sqlite3.Row
        db.execute_query("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        db.execute_query("INSERT INTO test (name) VALUES (?)", ("Bob",))
        result = db.execute_single_query("SELECT * FROM test WHERE name = ?", ("Bob",))
        assert result is not None
        assert result["name"] == "Bob"
        db.disconnect()

    def test_execute_single_query_no_result(self):
        """TC-6.7: Single query returns None when no match"""
        db = DatabaseManager()
        db.connection = sqlite3.connect(":memory:")
        db.connection.row_factory = sqlite3.Row
        db.execute_query("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        result = db.execute_single_query("SELECT * FROM test WHERE name = ?", ("Nobody",))
        assert result is None
        db.disconnect()


class TestAuthSystem:
    """Test the AuthSystem class"""

    @pytest.fixture(autouse=True)
    def setup_auth(self, tmp_path):
        """Create a fresh AuthSystem with temp database for each test"""
        self.auth = AuthSystem()
        self.db_path = str(tmp_path / "test_auth.db")
        self.auth.db.database_path = self.db_path
        # Monkey-patch DATABASE_PATH used in connect()
        import auth_database
        self._orig_db_path = auth_database.DATABASE_PATH
        auth_database.DATABASE_PATH = self.db_path
        self.auth.initialize_database()
        yield
        self.auth.close_connection()
        auth_database.DATABASE_PATH = self._orig_db_path

    def test_initialize_database(self):
        """TC-6.8: Database initialization creates tables"""
        # Tables already created in fixture - verify they exist
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        assert "users" in tables
        assert "user_sessions" in tables

    def test_register_user(self):
        """TC-6.9: Register a new user successfully"""
        result = self.auth.register_user("John Doe", "johndoe", "john@example.com", "SecurePass123")
        assert result["success"] is True

    def test_register_duplicate_user(self):
        """TC-6.10: Duplicate registration fails"""
        self.auth.register_user("John Doe", "johndoe", "john@example.com", "SecurePass123")
        result = self.auth.register_user("Jane Doe", "johndoe", "jane@example.com", "SecurePass456")
        assert result["success"] is False

    def test_register_short_password(self):
        """TC-6.11: Short password fails validation"""
        result = self.auth.register_user("John Doe", "johndoe", "john@example.com", "12345")
        assert result["success"] is False

    def test_register_short_username(self):
        """TC-6.12: Short username fails validation"""
        result = self.auth.register_user("John Doe", "jd", "john@example.com", "ValidPass123")
        assert result["success"] is False

    def test_register_invalid_email(self):
        """TC-6.13: Invalid email fails validation"""
        result = self.auth.register_user("John Doe", "johndoe", "notanemail", "ValidPass123")
        assert result["success"] is False

    def test_login_user_success(self):
        """TC-6.14: Login with valid credentials"""
        self.auth.register_user("John Doe", "johndoe", "john@example.com", "SecurePass123")
        result = self.auth.login_user("johndoe", "SecurePass123")
        assert result["success"] is True
        assert "token" in result

    def test_login_with_email(self):
        """TC-6.15: Login with email instead of username"""
        self.auth.register_user("John Doe", "johndoe", "john@example.com", "SecurePass123")
        result = self.auth.login_user("john@example.com", "SecurePass123")
        assert result["success"] is True

    def test_login_wrong_password(self):
        """TC-6.16: Login with wrong password fails"""
        self.auth.register_user("John Doe", "johndoe", "john@example.com", "SecurePass123")
        result = self.auth.login_user("johndoe", "WrongPassword")
        assert result["success"] is False

    def test_login_nonexistent_user(self):
        """TC-6.17: Login with non-existent user fails"""
        result = self.auth.login_user("nonexistent", "SomePass123")
        assert result["success"] is False

    def test_hash_password(self):
        """TC-6.18: Password hashing produces valid bcrypt hash"""
        hashed = self.auth.hash_password("TestPassword123")
        assert hashed.startswith("$2")  # bcrypt prefix
        assert len(hashed) > 50

    def test_verify_password(self):
        """TC-6.19: Password verification works correctly"""
        hashed = self.auth.hash_password("TestPassword123")
        assert self.auth.verify_password("TestPassword123", hashed) is True
        assert self.auth.verify_password("WrongPassword", hashed) is False

    def test_generate_jwt_token(self):
        """TC-6.20: JWT token generation"""
        token = self.auth.generate_jwt_token({
            "id": 1, "username": "testuser", "email": "test@example.com"
        })
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long

    def test_verify_jwt_token(self):
        """TC-6.21: JWT token verification roundtrip"""
        user_data = {"id": 1, "username": "testuser", "email": "test@example.com"}
        token = self.auth.generate_jwt_token(user_data)
        payload = self.auth.verify_jwt_token(token)
        assert payload is not None
        assert payload["username"] == "testuser"
        assert payload["user_id"] == 1

    def test_verify_invalid_jwt(self):
        """TC-6.22: Invalid JWT returns None"""
        result = self.auth.verify_jwt_token("invalid.token.here")
        assert result is None

    def test_get_user_by_token(self):
        """TC-6.23: Get user info from valid token"""
        self.auth.register_user("John Doe", "johndoe", "john@example.com", "SecurePass123")
        login_result = self.auth.login_user("johndoe", "SecurePass123")
        token = login_result["token"]
        user = self.auth.get_user_by_token(token)
        assert user is not None
        assert user["username"] == "johndoe"

    def test_logout_user(self):
        """TC-6.24: Logout invalidates session"""
        self.auth.register_user("John Doe", "johndoe", "john@example.com", "SecurePass123")
        login_result = self.auth.login_user("johndoe", "SecurePass123")
        token = login_result["token"]
        result = self.auth.logout_user(token)
        assert result is True

    def test_cleanup_expired_sessions(self):
        """TC-6.25: Cleanup expired sessions runs without error"""
        result = self.auth.cleanup_expired_sessions()
        # Should return True (successful query execution)
        assert result is True
