from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import jwt
import bcrypt
from datetime import datetime, timedelta
import uuid

router = APIRouter()
security = HTTPBearer()

# Mock user database (in real app, use proper database)
MOCK_USERS = {
    "test@example.com": {
        "id": "user_123",
        "email": "test@example.com", 
        "name": "Test User",
        "password_hash": bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "created_at": "2024-01-01T00:00:00Z"
    },
    "admin@crypto.com": {
        "id": "admin_456",
        "email": "admin@crypto.com",
        "name": "Admin User", 
        "password_hash": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "created_at": "2024-01-01T00:00:00Z"
    }
}

# JWT Settings
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    createdAt: str

class LoginResponse(BaseModel):
    user: UserResponse
    token: str
    message: str

def create_access_token(user_id: str, email: str) -> str:
    """Create JWT access token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """User login endpoint"""
    user = MOCK_USERS.get(login_data.email)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    token = create_access_token(user["id"], user["email"])
    
    # Return user data and token
    return LoginResponse(
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            createdAt=user["created_at"]
        ),
        token=token,
        message="Login successful"
    )

@router.post("/register", response_model=LoginResponse)
async def register(register_data: RegisterRequest):
    """User registration endpoint"""
    # Check if user already exists
    if register_data.email in MOCK_USERS:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = bcrypt.hashpw(register_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create new user
    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "email": register_data.email,
        "name": register_data.name,
        "password_hash": password_hash,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    # Add to mock database
    MOCK_USERS[register_data.email] = new_user
    
    # Create access token
    token = create_access_token(user_id, register_data.email)
    
    # Return user data and token
    return LoginResponse(
        user=UserResponse(
            id=user_id,
            email=register_data.email,
            name=register_data.name,
            createdAt=new_user["created_at"]
        ),
        token=token,
        message="Registration successful"
    )

@router.post("/logout")
async def logout():
    """User logout endpoint"""
    return {"message": "Logout successful"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user information"""
    try:
        # Decode JWT token
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        user_email = payload.get("email")
        user = MOCK_USERS.get(user_email)
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            createdAt=user["created_at"]
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh access token"""
    try:
        # Decode current token
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        user_id = payload.get("user_id")
        user_email = payload.get("email")
        
        # Create new token
        new_token = create_access_token(user_id, user_email)
        
        return {"token": new_token, "message": "Token refreshed successfully"}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
