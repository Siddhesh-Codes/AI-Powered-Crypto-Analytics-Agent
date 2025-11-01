"""
AI Chatbot API Endpoints
Provides REST API for AI-powered crypto chatbot with ML predictions
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os

# Import chatbot service
try:
    from app.services.ai_chatbot import get_chatbot
    CHATBOT_AVAILABLE = True
except ImportError:
    print("⚠️ Chatbot service not available")
    CHATBOT_AVAILABLE = False

router = APIRouter()


# Request/Response Models
class ChatMessage(BaseModel):
    """Chat message model"""
    message: str = Field(..., description="User's message to the chatbot")
    user_id: Optional[str] = Field(None, description="Optional user identifier")


class ChatResponse(BaseModel):
    """Chat response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    intent: Optional[str] = None
    symbol: Optional[str] = None
    timestamp: str


class PredictionRequest(BaseModel):
    """Price prediction request"""
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTC, ETH)")
    days_ahead: Optional[int] = Field(7, description="Number of days to predict ahead", ge=1, le=30)


class ModelInfoResponse(BaseModel):
    """Model information response"""
    ml_available: bool
    model_loaded: bool
    model_info: Optional[Dict[str, Any]] = None


class ChatHistoryResponse(BaseModel):
    """Chat history response"""
    history: List[Dict[str, Any]]
    count: int


# API Endpoints
@router.post("/chat", response_model=ChatResponse, tags=["AI Chat"])
async def chat_with_ai(request: ChatMessage):
    """
    Chat with AI assistant
    
    Send a message to the AI chatbot and get an intelligent response.
    The chatbot can:
    - Predict cryptocurrency prices using ML models
    - Provide technical analysis
    - Answer questions about cryptocurrencies
    - Give market insights
    
    **Example messages:**
    - "Predict Bitcoin price"
    - "Analyze Ethereum"
    - "What's the current price of BTC?"
    - "Tell me about Solana"
    """
    if not CHATBOT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Chatbot service is not available"
        )
    
    try:
        # Get chatbot instance
        groq_api_key = os.getenv("GROQ_API_KEY")
        bot = get_chatbot(groq_api_key=groq_api_key)
        
        # Process message
        response = await bot.chat(request.message, request.user_id)
        
        return ChatResponse(**response)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )


@router.post("/predict", response_model=ChatResponse, tags=["AI Chat"])
async def predict_price(request: PredictionRequest):
    """
    Get ML-based price prediction for a cryptocurrency
    
    Uses trained machine learning models to predict future price movements.
    
    **Supported cryptocurrencies:**
    BTC, ETH, XRP, ADA, SOL, DOGE, BNB, DOT, MATIC, LTC, and more
    """
    if not CHATBOT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Chatbot service is not available"
        )
    
    try:
        # Get chatbot instance
        groq_api_key = os.getenv("GROQ_API_KEY")
        bot = get_chatbot(groq_api_key=groq_api_key)
        
        # Generate prediction message
        message = f"Predict {request.symbol} price for {request.days_ahead} days"
        
        # Process through chatbot
        response = await bot.chat(message)
        
        return ChatResponse(**response)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating prediction: {str(e)}"
        )


@router.get("/model-info", response_model=ModelInfoResponse, tags=["AI Chat"])
async def get_model_info():
    """
    Get information about the ML model
    
    Returns details about the loaded machine learning model including:
    - Model type (Random Forest, Gradient Boosting, etc.)
    - Training date
    - Model accuracy
    - Number of features
    """
    if not CHATBOT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Chatbot service is not available"
        )
    
    try:
        from app.services.ml_predictor import ml_predictor
        
        model_info = ml_predictor.get_model_info()
        
        return ModelInfoResponse(
            ml_available=True,
            model_loaded=model_info.get('loaded', False),
            model_info=model_info if model_info.get('loaded') else None
        )
        
    except Exception as e:
        return ModelInfoResponse(
            ml_available=False,
            model_loaded=False,
            model_info=None
        )


@router.get("/history", response_model=ChatHistoryResponse, tags=["AI Chat"])
async def get_chat_history(limit: int = 10):
    """
    Get recent chat history
    
    Retrieves the most recent chat messages and responses.
    """
    if not CHATBOT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Chatbot service is not available"
        )
    
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        bot = get_chatbot(groq_api_key=groq_api_key)
        
        history = bot.get_chat_history(limit=limit)
        
        return ChatHistoryResponse(
            history=history,
            count=len(history)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        )


@router.delete("/history", tags=["AI Chat"])
async def clear_chat_history():
    """
    Clear chat history
    
    Clears all stored chat messages.
    """
    if not CHATBOT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Chatbot service is not available"
        )
    
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        bot = get_chatbot(groq_api_key=groq_api_key)
        
        bot.clear_history()
        
        return {
            "success": True,
            "message": "Chat history cleared"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing chat history: {str(e)}"
        )


@router.get("/supported-cryptos", tags=["AI Chat"])
async def get_supported_cryptos():
    """
    Get list of supported cryptocurrencies
    
    Returns a list of cryptocurrency symbols that the chatbot can analyze.
    """
    if not CHATBOT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Chatbot service is not available"
        )
    
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        bot = get_chatbot(groq_api_key=groq_api_key)
        
        return {
            "success": True,
            "cryptos": bot.supported_cryptos,
            "count": len(bot.supported_cryptos)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving supported cryptocurrencies: {str(e)}"
        )
