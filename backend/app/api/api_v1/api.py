from fastapi import APIRouter
from .endpoints import auth, ai_chat

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include AI chat routes
api_router.include_router(ai_chat.router, prefix="/ai", tags=["ai-chatbot"])

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

@api_router.get("/crypto/listings")
async def get_crypto_listings():
    """Get cryptocurrency listings"""
    # Mock data for now
    return {
        "data": [
            {
                "id": 1,
                "name": "Bitcoin",
                "symbol": "BTC",
                "quote": {
                    "USD": {
                        "price": 45000,
                        "percent_change_24h": 2.5
                    }
                }
            },
            {
                "id": 2,
                "name": "Ethereum",
                "symbol": "ETH",
                "quote": {
                    "USD": {
                        "price": 2500,
                        "percent_change_24h": 1.8
                    }
                }
            }
        ]
    }
