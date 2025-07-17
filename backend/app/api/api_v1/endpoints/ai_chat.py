"""
AI Chatbot API Endpoints
Real-time intelligent responses for crypto questions
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json

from ..services.ai_chatbot import ai_chatbot

router = APIRouter()

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict]] = []
    user_context: Optional[Dict] = {}

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime
    source: str  # "groq", "huggingface", or "enhanced_local"
    suggestions: Optional[List[str]] = []

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Chat with real AI - gets intelligent, dynamic responses
    """
    try:
        # Get AI response
        ai_response = await ai_chatbot.get_ai_response(
            user_message=request.message,
            conversation_history=request.conversation_history
        )
        
        # Generate contextual suggestions
        suggestions = generate_suggestions(request.message, ai_response)
        
        # Determine source
        source = "enhanced_local"  # Will be dynamic based on which AI responded
        if ai_chatbot.groq_api_key:
            source = "groq"
        elif ai_chatbot.huggingface_api_key:
            source = "huggingface"
        
        return ChatResponse(
            response=ai_response,
            timestamp=datetime.now(),
            source=source,
            suggestions=suggestions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.get("/chat/health")
async def health_check():
    """Check AI service health"""
    return {
        "status": "online",
        "ai_services": {
            "groq": bool(ai_chatbot.groq_api_key),
            "huggingface": bool(ai_chatbot.huggingface_api_key),
            "local_ai": True
        },
        "timestamp": datetime.now()
    }

def generate_suggestions(user_message: str, ai_response: str) -> List[str]:
    """Generate contextual follow-up suggestions"""
    
    message_lower = user_message.lower()
    
    if "bitcoin" in message_lower or "btc" in message_lower:
        return [
            "Show Bitcoin technical analysis",
            "Compare Bitcoin vs Ethereum", 
            "Bitcoin price predictions",
            "Best Bitcoin buying strategy"
        ]
    elif "portfolio" in message_lower:
        return [
            "Optimize my portfolio",
            "Calculate portfolio risk",
            "Rebalancing strategy",
            "Add new crypto to portfolio"
        ]
    elif "market" in message_lower:
        return [
            "Market sentiment analysis",
            "Best altcoins right now",
            "Market trend predictions",
            "When to buy the dip"
        ]
    elif any(word in message_lower for word in ["calculate", "profit", "loss"]):
        return [
            "DCA calculator",
            "Profit/loss analysis",
            "Tax implications",
            "Risk/reward ratio"
        ]
    else:
        return [
            "Analyze Bitcoin",
            "Review my portfolio", 
            "Market outlook",
            "Investment strategy"
        ]
