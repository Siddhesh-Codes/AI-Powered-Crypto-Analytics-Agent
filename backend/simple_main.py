from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI(title="Crypto Analytics API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for requests
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

# Simple in-memory storage (for demo purposes)
users_db = {}

@app.get("/")
async def root():
    return {"message": "Crypto Analytics API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    print(f"Registration attempt: {request.email}")
    # Check if user already exists
    if request.email in users_db:
        print(f"User {request.email} already exists")
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "name": request.name,
        "email": request.email,
        "password": request.password,  # In production, hash this!
        "createdAt": datetime.now().isoformat()
    }
    
    users_db[request.email] = user
    print(f"User {request.email} registered successfully. Total users: {len(users_db)}")
    
    # Generate mock token
    token = f"mock_token_{user_id}"
    
    return {
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "createdAt": user["createdAt"]
        },
        "token": token
    }

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    print(f"Login attempt: {request.email}")
    print(f"Available users: {list(users_db.keys())}")
    
    # Check if user exists
    if request.email not in users_db:
        print(f"User {request.email} not found")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = users_db[request.email]
    
    # Check password (in production, use proper hashing!)
    if user["password"] != request.password:
        print(f"Invalid password for {request.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    print(f"Login successful for {request.email}")
    # Generate mock token
    token = f"mock_token_{user['id']}"
    
    return {
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "createdAt": user["createdAt"]
        },
        "token": token
    }

@app.get("/api/v1/crypto/listings")
async def get_listings():
    return {
        "data": [
            {
                "id": 1,
                "name": "Bitcoin",
                "symbol": "BTC",
                "slug": "bitcoin",
                "cmc_rank": 1,
                "circulating_supply": 19500000,
                "total_supply": 19500000,
                "max_supply": 21000000,
                "quote": {
                    "USD": {
                        "price": 45200.23,
                        "volume_24h": 25000000000,
                        "percent_change_1h": 0.5,
                        "percent_change_24h": 2.73,
                        "percent_change_7d": 8.5,
                        "market_cap": 881000000000,
                        "last_updated": "2025-01-03T12:00:00Z"
                    }
                }
            },
            {
                "id": 2,
                "name": "Ethereum", 
                "symbol": "ETH",
                "slug": "ethereum",
                "cmc_rank": 2,
                "circulating_supply": 120000000,
                "total_supply": 120000000,
                "max_supply": None,
                "quote": {
                    "USD": {
                        "price": 2520.45,
                        "volume_24h": 15000000000,
                        "percent_change_1h": 1.2,
                        "percent_change_24h": 2.86,
                        "percent_change_7d": 12.3,
                        "market_cap": 302000000000,
                        "last_updated": "2025-01-03T12:00:00Z"
                    }
                }
            },
            {
                "id": 3,
                "name": "Cardano",
                "symbol": "ADA",
                "slug": "cardano",
                "cmc_rank": 3,
                "circulating_supply": 35000000000,
                "total_supply": 45000000000,
                "max_supply": 45000000000,
                "quote": {
                    "USD": {
                        "price": 0.52,
                        "volume_24h": 500000000,
                        "percent_change_1h": 0.8,
                        "percent_change_24h": 4.0,
                        "percent_change_7d": 15.2,
                        "market_cap": 18200000000,
                        "last_updated": "2025-01-03T12:00:00Z"
                    }
                }
            },
            {
                "id": 4,
                "name": "Solana",
                "symbol": "SOL",
                "slug": "solana",
                "cmc_rank": 4,
                "circulating_supply": 400000000,
                "total_supply": 500000000,
                "max_supply": None,
                "quote": {
                    "USD": {
                        "price": 95.23,
                        "volume_24h": 2000000000,
                        "percent_change_1h": 2.1,
                        "percent_change_24h": 3.26,
                        "percent_change_7d": 18.7,
                        "market_cap": 38000000000,
                        "last_updated": "2025-01-03T12:00:00Z"
                    }
                }
            }
        ]
    }

@app.get("/api/v1/crypto/global-metrics")
async def get_global_metrics():
    return {
        "data": {
            "active_cryptocurrencies": 9950,
            "total_cryptocurrencies": 25000,
            "btc_dominance": 45.2,
            "eth_dominance": 15.5,
            "quote": {
                "USD": {
                    "total_market_cap": 1950000000000,
                    "total_volume_24h": 85000000000,
                    "total_market_cap_yesterday_percentage_change": 1.56,
                    "total_volume_24h_yesterday_percentage_change": 3.66,
                    "last_updated": "2025-01-03T12:00:00Z"
                }
            }
        }
    }

@app.get("/api/v1/crypto/quote/{symbol}")
async def get_crypto_quote(symbol: str):
    # Mock data for any requested symbol
    crypto_data = {
        "BTC": {"name": "Bitcoin", "price": 45200.23, "change_24h": 2.73},
        "ETH": {"name": "Ethereum", "price": 2520.45, "change_24h": 2.86},
        "ADA": {"name": "Cardano", "price": 0.52, "change_24h": 4.0},
        "SOL": {"name": "Solana", "price": 95.23, "change_24h": 3.26},
    }
    
    symbol_upper = symbol.upper()
    if symbol_upper in crypto_data:
        data = crypto_data[symbol_upper]
        return {
            "data": {
                "id": 1,
                "name": data["name"],
                "symbol": symbol_upper,
                "quote": {
                    "USD": {
                        "price": data["price"],
                        "percent_change_24h": data["change_24h"],
                        "last_updated": "2025-01-03T12:00:00Z"
                    }
                }
            }
        }
    else:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")

@app.get("/api/v1/crypto/search")
async def search_crypto(q: str):
    # Simple search implementation
    all_cryptos = [
        {"id": 1, "name": "Bitcoin", "symbol": "BTC"},
        {"id": 2, "name": "Ethereum", "symbol": "ETH"},
        {"id": 3, "name": "Cardano", "symbol": "ADA"},
        {"id": 4, "name": "Solana", "symbol": "SOL"},
    ]
    
    query = q.lower()
    results = [
        crypto for crypto in all_cryptos 
        if query in crypto["name"].lower() or query in crypto["symbol"].lower()
    ]
    
    return {"data": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
