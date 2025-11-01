from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict, Any
import uvicorn
import os
import asyncio
import random
import re
import smtplib
import secrets
import hashlib
import jwt
import json
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from auth_database import auth_system, init_auth_database
from technical_indicators import TechnicalIndicators, CryptoDataFetcher, analyze_technical_indicators
# Temporarily disabled due to scipy import issues
# from news_sentiment import news_client, sentiment_analyzer
news_client = None
sentiment_analyzer = None
from websocket_manager import websocket_manager, SubscriptionType
from fastapi import WebSocket, WebSocketDisconnect
import aiohttp
import time
from typing import Optional

# Price caching system
PRICE_CACHE = {}
CACHE_DURATION = 120  # 2 minutes cache

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables")

# Create FastAPI instance
app = FastAPI(
    title="Crypto Analytics Agent API",
    description="AI-Powered Cryptocurrency Analytics and Forecasting API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global background tasks
background_tasks = set()

@app.on_event("startup")
async def startup_event():
    """Initialize background tasks on startup"""
    print("🚀 Initializing background services...")
    
    # Start global price monitoring task for alerts
    task = asyncio.create_task(monitor_price_alerts())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
    
    print("✅ Background alert monitoring started")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    print("🛑 Shutting down background services...")
    
    # Cancel all background tasks
    for task in background_tasks:
        task.cancel()
    
    # Wait for tasks to finish
    await asyncio.gather(*background_tasks, return_exceptions=True)
    
    print("✅ Background services stopped")

# Authentication and Email Configuration
security = HTTPBearer()

# Authentication system now uses MySQL database
# No more in-memory storage or OTP needed

# Pydantic models for MySQL authentication
class UserRegistration(BaseModel):
    name: str
    username: str
    email: str
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Please enter a valid email address')
        return v

class UserLogin(BaseModel):
    login: str  # Can be username or email
    password: str

class AuthResponse(BaseModel):
    message: str
    success: bool
    token: Optional[str] = None
    user: Optional[Dict[str, Any]] = None

# Security setup
security = HTTPBearer(auto_error=False)

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from JWT token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_system.get_user_by_token(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and authentication system on startup"""
    print("🚀 Starting Crypto Analytics Backend...")
    
    # Initialize authentication database
    if init_auth_database():
        print("✅ Authentication system initialized successfully!")
    else:
        print("❌ Failed to initialize authentication system!")
    
    # Cleanup expired sessions
    auth_system.cleanup_expired_sessions()
    print("🧹 Cleaned up expired user sessions")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    auth_system.close_connection()
    print("👋 Backend shutdown complete")

# OTP functions removed - now using MySQL database authentication

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, Any]]] = []
    user_context: Optional[Dict[str, Any]] = {}

class ChatResponse(BaseModel):
    response: str
    source: str
    suggestions: Optional[List[str]] = []
    
# Global variables for AI service
AI_SERVICE_AVAILABLE = False
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize AI service variables
AI_SERVICE_AVAILABLE = False
groq_client = None

# Try to import and initialize Groq
try:
    import groq
    if GROQ_API_KEY:
        groq_client = groq.Groq(api_key=GROQ_API_KEY)
        AI_SERVICE_AVAILABLE = True
        print("✅ Groq AI service initialized successfully!")
    else:
        print("⚠️ GROQ_API_KEY not found in environment variables")
        print("💡 Using enhanced fallback AI responses instead")
except ImportError:
    print("⚠️ Groq library not installed. Using enhanced fallback AI responses")
except Exception as e:
    print(f"⚠️ Error initializing Groq: {e}")
    print("💡 Using enhanced fallback AI responses instead")

# Real-time cryptocurrency price fetching
async def fetch_crypto_price(crypto_id: str = "bitcoin") -> Dict[str, Any]:
    """
    Fetch real-time cryptocurrency price from CoinGecko API
    crypto_id examples: bitcoin, ethereum, binancecoin, cardano, solana, etc.
    """
    try:
        # Get IST timezone
        ist_timezone = timezone(timedelta(hours=5, minutes=30))
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if crypto_id in data:
                        price_data = data[crypto_id]
                        return {
                            "success": True,
                            "price": price_data.get("usd", 0),
                            "price_change_24h": price_data.get("usd_24h_change", 0),
                            "market_cap": price_data.get("usd_market_cap", 0),
                            "timestamp": datetime.now(ist_timezone).isoformat()
                        }
                    else:
                        return {"success": False, "error": f"Cryptocurrency '{crypto_id}' not found"}
                else:
                    return {"success": False, "error": f"API request failed with status {response.status}"}
    except Exception as e:
        return {"success": False, "error": f"Failed to fetch price: {str(e)}"}

async def get_live_crypto_price(crypto_symbol: str) -> Optional[Dict[str, Any]]:
    """Get live crypto price from CoinGecko API with caching"""
    
    crypto_symbol = crypto_symbol.upper()
    current_time = time.time()
    
    # Check cache first
    if crypto_symbol in PRICE_CACHE:
        cached_data, timestamp = PRICE_CACHE[crypto_symbol]
        if current_time - timestamp < CACHE_DURATION:
            print(f"✅ Using cached price for {crypto_symbol}: ${cached_data['price']:,.2f}")
            return cached_data
    
    # Map symbols to CoinGecko IDs
    symbol_to_id = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum', 
        'SOL': 'solana',
        'ADA': 'cardano',
        'MATIC': 'polygon',
        'AVAX': 'avalanche-2',
        'LINK': 'chainlink',
        'XRP': 'ripple',
        'DOT': 'polkadot',
        'ATOM': 'cosmos'
    }
    
    if crypto_symbol not in symbol_to_id:
        print(f"❌ Unsupported crypto symbol: {crypto_symbol}")
        return None
    
    crypto_id = symbol_to_id[crypto_symbol]
    
    try:
        print(f"🔄 Fetching live price for {crypto_symbol} from CoinGecko...")
        print(f"🔍 [DEBUG] Mapping {crypto_symbol} to {crypto_id}")
        async with aiohttp.ClientSession() as session:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd&include_24hr_change=true"
            print(f"🔍 [DEBUG] API URL: {url}")
            
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if crypto_id in data:
                        price_data = {
                            'symbol': crypto_symbol,
                            'name': symbol_to_id[crypto_symbol].replace('-', ' ').title(),
                            'price': data[crypto_id]['usd'],
                            'change_24h': data[crypto_id].get('usd_24h_change', 0)
                        }
                        
                        # Cache the result
                        PRICE_CACHE[crypto_symbol] = (price_data, current_time)
                        
                        print(f"✅ Live price fetched for {crypto_symbol}: ${price_data['price']:,.2f}")
                        return price_data
                else:
                    print(f"❌ CoinGecko API returned status {response.status}")
                    
    except Exception as e:
        print(f"❌ Error fetching live price for {crypto_symbol}: {e}")
    
    return None

async def get_multiple_crypto_prices(crypto_ids: List[str]) -> Dict[str, Any]:
    """
    Fetch prices for multiple cryptocurrencies at once
    """
    try:
        # Get IST timezone
        ist_timezone = timezone(timedelta(hours=5, minutes=30))
        ids_string = ",".join(crypto_ids)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_string}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    formatted_data = {}
                    for crypto_id in crypto_ids:
                        if crypto_id in data:
                            price_data = data[crypto_id]
                            formatted_data[crypto_id] = {
                                "price": price_data.get("usd", 0),
                                "price_change_24h": price_data.get("usd_24h_change", 0),
                                "market_cap": price_data.get("usd_market_cap", 0)
                            }
                    
                    return {
                        "success": True,
                        "data": formatted_data,
                        "timestamp": datetime.now(ist_timezone).isoformat()
                    }
                else:
                    return {"success": False, "error": f"API request failed with status {response.status}"}
    except Exception as e:
        return {"success": False, "error": f"Failed to fetch prices: {str(e)}"}

async def get_real_ai_response(user_message: str, context: Dict[str, Any] = {}) -> str:
    """Get response from Groq AI with LIVE price data integration for accuracy"""
    if not AI_SERVICE_AVAILABLE:
        raise Exception("AI service not available")
    
    try:
        # Always detect crypto mentions first
        crypto_mentions = detect_crypto_mentions(user_message)
        print(f"🔍 [DEBUG] User message: '{user_message}'")
        print(f"🔍 [DEBUG] Crypto mentions: {crypto_mentions}")
        
        # Fetch live price data for any mentioned cryptos
        live_price_context = ""
        if crypto_mentions:
            print(f"🔍 [DEBUG] Fetching live prices for: {crypto_mentions}")
            live_prices = []
            
            for crypto in crypto_mentions:
                # Convert crypto name to symbol - FIXED VERSION
                name_to_symbol = {
                    'BITCOIN': 'BTC', 'ETHEREUM': 'ETH', 'SOLANA': 'SOL',
                    'CARDANO': 'ADA', 'POLYGON': 'MATIC', 'POLKADOT': 'DOT',
                    'CHAINLINK': 'LINK', 'COSMOS': 'ATOM', 'ALGORAND': 'ALGO',
                    'UNISWAP': 'UNI'
                }
                
                print(f"🔍 [DEBUG] Converting crypto: '{crypto}' -> symbol")
                crypto_symbol = name_to_symbol.get(crypto, crypto)
                print(f"🔍 [DEBUG] Final symbol: '{crypto_symbol}'")
                
                live_data = await get_live_crypto_price(crypto_symbol)
                
                if live_data:
                    live_prices.append(f"{live_data['name']} ({crypto_symbol}): ${live_data['price']:,.2f} ({live_data['change_24h']:+.1f}% 24h)")
                    print(f"✅ Live price fetched: {live_data['name']} = ${live_data['price']:,.2f}")
            
            if live_prices:
                live_price_context = f"\n\nCURRENT LIVE MARKET PRICES (Use these EXACT prices - ignore any other price data):\n" + "\n".join(live_prices)
                print(f"� [DEBUG] Live price context added: {len(live_prices)} cryptos")
        
        # Analyze question complexity to determine response length
        complexity = analyze_question_complexity(user_message)
        
        # Create enhanced system prompt that FORCES use of live price data
        base_system_prompt = """You are a professional cryptocurrency analyst with access to LIVE market data.

CRITICAL INSTRUCTIONS:
- ALWAYS use the EXACT live price data provided in the context when discussing ANY cryptocurrency prices
- NEVER use outdated prices from your training data
- If live price data is provided, that is the ONLY correct price - ignore all other price information
- Provide accurate, current information based on the live data"""

        if complexity == "simple":
            system_prompt = base_system_prompt + """
            
Response style: Keep responses under 50 words. Be direct and professional. No emojis. No markdown formatting."""
            max_tokens = 150
        elif complexity == "medium":
            system_prompt = base_system_prompt + """
            
Response style: Provide informative analysis in 2-3 sentences. Professional tone. No markdown formatting.
Keep responses under 150 words. Be clear and structured."""
            max_tokens = 200
        else:  # complex
            system_prompt = """You are an expert cryptocurrency analyst with access to live market data.
            Always use the EXACT live price data provided in the context when discussing prices.
            Provide comprehensive, data-driven insights about crypto markets, trading strategies, 
            portfolio analysis, and blockchain technology. Give practical, actionable advice 
            while mentioning this is not financial advice. Be thorough but well-structured. Use NO markdown."""
            max_tokens = 400
        
        # Add context if available
        context_str = ""
        if context.get("portfolio_value"):
            context_str += f"User's portfolio value: ${context['portfolio_value']:,.2f}\n"
        if context.get("portfolio_change"):
            context_str += f"24h portfolio change: {context['portfolio_change']:.2f}%\n"
        if context.get("top_cryptos"):
            context_str += f"Current top cryptos in portfolio: {[crypto.get('symbol', '') for crypto in context.get('top_cryptos', [])]}\n"
        
        # Combine context with live price data
        final_context = context_str + live_price_context
        
        # Create final prompt with live price data
        full_prompt = f"{final_context}\n\nUser question: {user_message}"
        
        print(f"🔍 [DEBUG] Final context sent to AI:\n{final_context}")
        print(f"🔍 [DEBUG] Full prompt length: {len(full_prompt)} chars")
        
        # Call Groq API with live price data
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=max_tokens
        )
        
        ai_response = completion.choices[0].message.content.strip()
        clean_response = clean_markdown_response(ai_response)
        
        print(f"✅ [SUCCESS] AI response generated with live price integration")
        return clean_response
        
    except Exception as e:
        print(f"❌ [ERROR] Groq API failed: {e}")
        raise Exception(f"AI service error: {str(e)}")

async def get_enhanced_fallback_response(user_message: str, context: Dict[str, Any] = {}) -> str:
    """Dynamic AI that analyzes questions and generates intelligent responses with smart length control"""
    await asyncio.sleep(0.8)  # Simulate AI thinking time
    
    # Get IST time (UTC + 5:30)
    ist_timezone = timezone(timedelta(hours=5, minutes=30))
    timestamp = datetime.now(ist_timezone).strftime("%H:%M")
    
    # Analyze question complexity first
    complexity = analyze_question_complexity(user_message)
    
    # Analyze the user's question intelligently
    analysis = analyze_user_question(user_message)
    
    # Fetch real-time price data if it's a price-related question
    real_time_data = {}
    if analysis["question_type"] == "price_analysis" and analysis["crypto_mentions"]:
        # Map crypto mentions to CoinGecko IDs
        crypto_id_map = {
            'BTC': 'bitcoin', 'BITCOIN': 'bitcoin',
            'ETH': 'ethereum', 'ETHEREUM': 'ethereum',
            'SOL': 'solana', 'SOLANA': 'solana',
            'ADA': 'cardano', 'CARDANO': 'cardano',
            'MATIC': 'polygon', 'POLYGON': 'polygon',
            'AVAX': 'avalanche', 'AVALANCHE': 'avalanche',
            'LINK': 'chainlink', 'CHAINLINK': 'chainlink'
        }
        
        # Fetch prices for mentioned cryptos
        crypto_ids_to_fetch = []
        for crypto in analysis["crypto_mentions"]:
            if crypto in crypto_id_map:
                crypto_ids_to_fetch.append(crypto_id_map[crypto])
        
        if crypto_ids_to_fetch:
            price_data = await get_multiple_crypto_prices(crypto_ids_to_fetch)
            real_time_data = price_data
    
    # Generate dynamic response based on analysis and complexity
    response = await generate_intelligent_response(user_message, analysis, timestamp, context, real_time_data, complexity)
    
    return clean_markdown_response(response)

def analyze_question_simple(text: str) -> Dict[str, Any]:
    """Simple analysis to detect question type"""
    text_lower = text.lower()
    
    # Price query patterns
    price_patterns = [
        r'\b(price|cost|value|worth)\b',
        r'\bhow\s+much\b',
        r'\bcurrent\s+price\b',
        r'\bwhat\s+(is|are)\s+.*(price|trading|worth)\b'
    ]
    
    for pattern in price_patterns:
        if re.search(pattern, text_lower):
            return {"question_type": "price_query"}
    
    return {"question_type": "general"}

def detect_crypto_mentions(text: str) -> List[str]:
    """Detect cryptocurrency mentions in text and return in uppercase format"""
    crypto_patterns = {
        'BITCOIN': ['bitcoin', 'btc'],
        'ETHEREUM': ['ethereum', 'eth', 'ether'],
        'SOLANA': ['solana', 'sol'],
        'CARDANO': ['cardano', 'ada'],
        'POLKADOT': ['polkadot', 'dot'],
        'POLYGON': ['polygon', 'matic'],
        'CHAINLINK': ['chainlink', 'link'],
        'UNISWAP': ['uniswap', 'uni'],
        'COSMOS': ['cosmos', 'atom'],
        'ALGORAND': ['algorand', 'algo'],
    }
    
    text_lower = text.lower()
    mentioned_cryptos = []
    
    for crypto_key, patterns in crypto_patterns.items():
        for pattern in patterns:
            if re.search(r'\b' + pattern + r'\b', text_lower):
                mentioned_cryptos.append(crypto_key)
                break
    
    return mentioned_cryptos

def analyze_question_simple(question: str) -> Dict[str, Any]:
    """Analyze question and return type information - FIXED VERSION"""
    question_lower = question.lower()
    
    # Detect crypto mentions first
    crypto_mentions = detect_crypto_mentions(question)
    has_crypto = len(crypto_mentions) > 0
    
    # Detect if it's a price question
    price_keywords = ['price', 'cost', 'value', 'worth', 'current', 'now', 'today']
    explanation_keywords = ['what is', 'explain', 'tell me about', 'describe', 'about']
    
    is_price_question = any(keyword in question_lower for keyword in price_keywords)
    is_explanation_question = any(keyword in question_lower for keyword in explanation_keywords)
    
    # CRITICAL FIX: If question mentions crypto AND is explanation/price, use live data path
    if has_crypto and (is_price_question or is_explanation_question):
        question_type = 'price_query'  # This forces live API usage
        print(f"🔍 [DEBUG] FIXED: Crypto explanation detected - routing to live API path")
    elif is_price_question:
        question_type = 'price_query'
    elif any(word in question_lower for word in ['analysis', 'trend', 'forecast']):
        question_type = 'analysis'
    else:
        question_type = 'general'
    
    return {
        'question_type': question_type,
        'is_price_question': is_price_question or (has_crypto and is_explanation_question),
        'complexity': 'simple' if (is_price_question or is_explanation_question) else 'medium'
    }

def analyze_question_complexity(question: str) -> str:
    """Analyze question complexity to determine response length"""
    question_lower = question.lower().strip()
    word_count = len(question.split())
    
    # Simple questions (short, direct)
    simple_patterns = [
        'price', 'cost', 'worth', 'value', 'current price', 'price now',
        'how much', 'what is', 'tell me', 'show me', 'give me'
    ]
    
    # Complex questions (detailed analysis needed)
    complex_patterns = [
        'explain', 'analyze', 'compare', 'strategy', 'investment advice',
        'portfolio', 'should i invest', 'risk assessment', 'technical analysis',
        'market analysis', 'forecast', 'prediction', 'future', 'long term'
    ]
    
    # Check for simple patterns and short questions
    if word_count <= 5 or any(pattern in question_lower for pattern in simple_patterns):
        # Exception: if it also contains complex terms, make it medium
        if any(pattern in question_lower for pattern in complex_patterns):
            return "medium"
        return "simple"
    
    # Check for complex patterns
    if any(pattern in question_lower for pattern in complex_patterns) or word_count > 15:
        return "complex"
    
    # Default to medium complexity
    return "medium"

def clean_markdown_response(response: str) -> str:
    """Clean ALL markdown formatting and return plain text"""
    if not response:
        return ""
    
    import re
    
    # Remove unwanted content patterns
    lines = response.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip lines with fake portfolio data or unwanted content
        if any(unwanted in line.lower() for unwanted in [
            "['btc',", "[btc,", "'btc'", "'eth'", "'xrp'",
            "btc, eth, xrp", "current portfolio", "your portfolio contains"
        ]):
            continue
        
        # Clean the line - remove ALL markdown formatting
        cleaned_line = line.strip()
        
        # Remove ALL markdown formatting
        # Remove bold (**text** and __text__)
        cleaned_line = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned_line)
        cleaned_line = re.sub(r'__(.*?)__', r'\1', cleaned_line)
        
        # Remove italic (*text* and _text_)
        cleaned_line = re.sub(r'\*(.*?)\*', r'\1', cleaned_line)
        cleaned_line = re.sub(r'_(.*?)_', r'\1', cleaned_line)
        
        # Remove headers (# ## ### etc)
        cleaned_line = re.sub(r'^#+\s*', '', cleaned_line)
        
        # Remove bullet points and convert to simple dashes
        cleaned_line = re.sub(r'^[\*\-\+]\s+', '- ', cleaned_line)
        cleaned_line = re.sub(r'^•\s+', '- ', cleaned_line)
        
        # Remove any remaining standalone asterisks
        cleaned_line = re.sub(r'\*', '', cleaned_line)
        
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    
    # Join lines back
    cleaned_response = '\n'.join(cleaned_lines)
    
    # Remove excessive newlines
    cleaned_response = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_response)
    
    return cleaned_response.strip()

def analyze_user_question(question: str) -> Dict[str, Any]:
    """Analyze user question to understand intent and topics"""
    
    question_lower = question.lower()
    
    # Extract key concepts and entities
    crypto_mentions = []
    for crypto in ['bitcoin', 'btc', 'ethereum', 'eth', 'solana', 'sol', 'cardano', 'ada', 'polygon', 'matic', 'chainlink', 'link', 'avalanche', 'avax']:
        if crypto in question_lower:
            crypto_mentions.append(crypto.upper())
    
    # Determine question type and intent
    question_type = "general"
    sentiment = "neutral"
    urgency = "normal"
    
    # Investment/Safety questions
    if any(word in question_lower for word in ['safe', 'invest', 'should i', 'risk', 'buy', 'worth it']):
        question_type = "investment_advice"
        
    # Price/Market questions  
    elif any(word in question_lower for word in ['price', 'cost', 'expensive', 'cheap', 'value', 'market', 'current price', 'price now', 'how much', 'worth']):
        question_type = "price_analysis"
        
    # Technical questions
    elif any(word in question_lower for word in ['how', 'what', 'explain', 'work', 'technology']):
        question_type = "educational"
        
    # Trading questions
    elif any(word in question_lower for word in ['trade', 'trading', 'strategy', 'when', 'timing']):
        question_type = "trading_advice"
        
    # Future/Prediction questions
    elif any(word in question_lower for word in ['future', 'predict', 'forecast', 'will', 'going to']):
        question_type = "prediction"
    
    # Detect sentiment
    if any(word in question_lower for word in ['worried', 'scared', 'afraid', 'concern', 'panic', 'crash']):
        sentiment = "fearful"
    elif any(word in question_lower for word in ['excited', 'bullish', 'moon', 'pump', 'opportunity']):
        sentiment = "optimistic"
        
    # Detect urgency
    if any(word in question_lower for word in ['urgent', 'quickly', 'asap', 'now', 'immediately']):
        urgency = "high"
    
    return {
        "question_type": question_type,
        "crypto_mentions": crypto_mentions,
        "sentiment": sentiment,
        "urgency": urgency,
        "question_length": len(question.split()),
        "contains_numbers": any(char.isdigit() for char in question)
    }

async def generate_intelligent_response(question: str, analysis: Dict[str, Any], timestamp: str, context: Dict[str, Any], real_time_data: Dict[str, Any] = {}, complexity: str = "medium") -> str:
    """Generate contextual, intelligent response based on question analysis and complexity"""
    
    question_type = analysis["question_type"]
    crypto_mentions = analysis["crypto_mentions"]
    sentiment = analysis["sentiment"]
    urgency = analysis["urgency"]
    
    # Build dynamic response based on complexity level
    response_parts = []
    
    # Simple responses - direct and brief
    if complexity == "simple":
        if question_type == "price_analysis" and crypto_mentions:
            return await generate_simple_price_response(crypto_mentions[0], real_time_data)
        elif question_type == "general" or not crypto_mentions:
            return "Professional crypto analysis available. Please specify which cryptocurrency or topic you'd like information about."
        else:
            return generate_simple_response(question, analysis, crypto_mentions)
    
    # Medium responses - structured but concise
    elif complexity == "medium":
        # Professional greeting without emojis for medium complexity
        response_parts.append(f"**Professional Analysis** • {timestamp}\n\n")
        
        # Generate focused content
        if question_type == "investment_advice":
            main_content = generate_medium_investment_advice(question, crypto_mentions, sentiment)
        elif question_type == "price_analysis":
            main_content = await generate_medium_price_analysis(question, crypto_mentions, real_time_data)
        elif question_type == "educational":
            main_content = generate_medium_educational_content(question, crypto_mentions)
        else:
            main_content = generate_medium_general_response(question, analysis)
        
        response_parts.append(main_content)
        
        # Brief closing
        response_parts.append("\n\n**Note:** This is educational information, not financial advice.")
    
    # Complex responses - detailed and comprehensive
    else:  # complex
        # Add professional greeting
        if sentiment == "fearful":
            greeting = "**Risk Assessment & Analysis**"
        elif sentiment == "optimistic":  
            greeting = "**Market Opportunity Analysis**"
        else:
            greeting = "**Comprehensive Crypto Analysis**"
        
        response_parts.append(f"{greeting} • {timestamp}\n\n")
        
        # Generate detailed content
        if question_type == "investment_advice":
            main_content = generate_investment_advice(question, crypto_mentions, sentiment)
        elif question_type == "price_analysis":
            main_content = generate_price_analysis(question, crypto_mentions, real_time_data)
        elif question_type == "educational":
            main_content = generate_educational_content(question, crypto_mentions)
        elif question_type == "trading_advice":
            main_content = generate_trading_advice(question, crypto_mentions)
        elif question_type == "prediction":
            main_content = generate_prediction_analysis(question, crypto_mentions)
        else:
            main_content = generate_general_crypto_response(question, analysis)
        
        response_parts.append(main_content)
        
        # Add contextual closing
        if urgency == "high":
            closing = "\n\n**Important Considerations:**\n• Start with small amounts to learn\n• Use reputable exchanges only\n• Never invest emergency funds\n• Take time to research properly"
        else:
            closing = "\n\n**Professional Disclaimer:** This analysis is for educational purposes only and should not be considered as financial advice. Always conduct your own research and consider your risk tolerance."
        
        response_parts.append(closing)
    
    # Join and return
    final_response = "".join(response_parts)
    return final_response

async def generate_simple_price_response(crypto_symbol: str, real_time_data: Dict[str, Any] = {}, question_type: str = "price") -> str:
    """Generate response with live API data - handles both price queries and explanations"""
    
    # Convert crypto name to symbol if needed
    name_to_symbol = {
        'BITCOIN': 'BTC',
        'ETHEREUM': 'ETH', 
        'SOLANA': 'SOL',
        'CARDANO': 'ADA',
        'POLYGON': 'MATIC',
        'POLKADOT': 'DOT',
        'CHAINLINK': 'LINK',
        'COSMOS': 'ATOM',
        'ALGORAND': 'ALGO',
        'UNISWAP': 'UNI'
    }
    
    crypto_key = crypto_symbol.upper()
    # Convert name to symbol if it's a full name
    if crypto_key in name_to_symbol:
        crypto_key = name_to_symbol[crypto_key]
    
    print(f"🔍 [DEBUG] generate_simple_price_response called for: {crypto_symbol} -> {crypto_key}")
    
    # Try to get live price first
    live_data = await get_live_crypto_price(crypto_key)
    print(f"🔍 [DEBUG] live_data result: {live_data}")
    
    if live_data:
        price = live_data['price']
        change = live_data['change_24h']
        name = live_data['name']
        
        # For explanation questions, provide brief overview with LIVE price
        if "explain" in question_type.lower() or "what is" in question_type.lower():
            return f"{name} (BTC) is the world's largest cryptocurrency by market capitalization. Current price: ${price:,.2f} ({change:+.1f}% 24h). It serves as digital gold and a store of value in the crypto ecosystem."
        
        # For simple price questions, just return price without trend commentary
        else:
            return f"{name} ({crypto_key}): ${price:,.2f} ({change:+.1f}% 24h)"
    
    else:
        # Fallback when API fails - but still try to be helpful
        return f"{crypto_key} price data temporarily unavailable due to API issues. Please try again in a moment or check a major exchange for current pricing."

def generate_simple_response(question: str, analysis: Dict[str, Any], crypto_mentions: list) -> str:
    """Generate simple response for non-price questions - plain text only"""
    
    question_type = analysis["question_type"]
    
    if question_type == "investment_advice":
        return "Investment guidance: Crypto investing involves high risk. Start with small amounts, use reputable exchanges, and never invest more than you can afford to lose."
    
    elif question_type == "educational":
        if crypto_mentions:
            crypto = crypto_mentions[0]
            return f"{crypto} is a cryptocurrency. For detailed technical information, please ask a more specific question about its technology or use case."
        return "Cryptocurrency education: Digital assets using blockchain technology. Ask about specific topics for detailed explanations."
    
    elif question_type == "trading_advice":
        return "Trading guidance: Use proper risk management, set stop-losses, and never trade with borrowed money. Market timing is extremely difficult."
    
    else:
        return "Professional Analysis Available. Please specify your question about cryptocurrency markets, investments, or technology."

def generate_medium_investment_advice(question: str, crypto_mentions: list, sentiment: str) -> str:
    """Generate medium-length investment advice"""
    
    advice_parts = []
    
    if "safe" in question.lower() or "risk" in question.lower():
        advice_parts.append("**Investment Risk Assessment:**\n\n")
        advice_parts.append("Cryptocurrency investing carries significant risks including extreme volatility, regulatory uncertainty, and technology risks. However, it can be part of a diversified portfolio.\n\n")
        advice_parts.append("**Recommended Approach:**\n")
        advice_parts.append("• Limit crypto to 5-10% of total investment portfolio\n")
        advice_parts.append("• Start with Bitcoin and Ethereum (lower risk cryptos)\n")
        advice_parts.append("• Use dollar-cost averaging over 6-12 months\n")
        advice_parts.append("• Only invest funds you can completely afford to lose")
    
    elif crypto_mentions:
        crypto = crypto_mentions[0]
        advice_parts.append(f"**{crypto} Investment Analysis:**\n\n")
        
        if crypto in ['BTC', 'BITCOIN']:
            advice_parts.append("Bitcoin is considered the lowest-risk cryptocurrency investment due to its established network, institutional adoption, and fixed supply. Good entry point for crypto beginners.\n\n")
            advice_parts.append("**Key factors:** Store of value narrative, ETF approvals, institutional adoption, and 4-year market cycles.")
        
        elif crypto in ['ETH', 'ETHEREUM']:
            advice_parts.append("Ethereum offers growth potential through its smart contract platform and DeFi ecosystem. Generates staking yield but more volatile than Bitcoin.\n\n")
            advice_parts.append("**Key factors:** DeFi leadership, NFT platform, staking rewards, and upcoming network upgrades.")
        
        else:
            advice_parts.append(f"{crypto} is a higher-risk investment compared to Bitcoin/Ethereum. Requires thorough research of the project's fundamentals.\n\n")
            advice_parts.append("**Due diligence:** Research team, technology, partnerships, tokenomics, and competitive advantages.")
    
    else:
        advice_parts.append("**General Investment Strategy:**\n\n")
        advice_parts.append("Focus on established cryptocurrencies for core holdings (70% Bitcoin/Ethereum), with smaller allocations to promising altcoins (30%).\n\n")
        advice_parts.append("**Strategy:** Long-term holding (3-5+ years), regular DCA purchases, and gradual profit-taking during market peaks.")
    
    return "".join(advice_parts)

async def generate_medium_price_analysis(question: str, crypto_mentions: list, real_time_data: Dict[str, Any] = {}) -> str:
    """Generate medium-length price analysis with live data - plain text"""
    
    if not crypto_mentions:
        return "Market Overview: Crypto markets showing mixed signals. Specify a particular cryptocurrency for detailed price analysis."
    
    crypto = crypto_mentions[0]
    
    # Try to get live price data
    live_data = await get_live_crypto_price(crypto)
    
    if not live_data:
        return f"{crypto} Analysis: Price data temporarily unavailable due to API issues. Please check major crypto exchanges for current pricing."
    
    price = live_data['price']
    change = live_data['change_24h']
    name = live_data['name']
    
    # Determine trend based on price change
    if change > 5:
        trend = "Strong bullish momentum"
        outlook = "Strong bullish momentum. Monitor for profit-taking at resistance levels."
    elif change > 2:
        trend = "Moderate upward movement"
        outlook = "Positive momentum building. Good for continued accumulation."
    elif change > -2:
        trend = "Sideways consolidation"
        outlook = "Consolidation phase. Good for range trading or continued DCA strategy."
    elif change > -5:
        trend = "Minor correction"
        outlook = "Minor pullback. Potential buying opportunity for long-term holders."
    else:
        trend = "Significant correction"
        outlook = "Major correction phase. High-risk, high-reward accumulation opportunity for experienced investors."
    
    # Plain text response without markdown
    analysis_parts = []
    analysis_parts.append(f"{name} ({crypto}) Analysis:\n\n")
    analysis_parts.append(f"Current Price: ${price:,.2f}\n")
    analysis_parts.append(f"24h Change: {change:+.1f}%\n")
    analysis_parts.append(f"Market Trend: {trend}\n\n")
    analysis_parts.append(f"Technical Outlook: {outlook}")
    
    return "".join(analysis_parts)

def generate_medium_educational_content(question: str, crypto_mentions: list) -> str:
    """Generate medium-length educational content"""
    
    if not crypto_mentions:
        return "**Cryptocurrency Education:** Digital assets using blockchain technology for decentralized transactions. Popular examples include Bitcoin (store of value), Ethereum (smart contracts), and various altcoins serving specific use cases."
    
    crypto = crypto_mentions[0]
    
    education_content = {
        'BTC': "**Bitcoin Education:** First cryptocurrency (2009) designed as digital gold. Uses proof-of-work consensus, has fixed supply of 21 million coins, and serves as a decentralized store of value without central authority.",
        
        'ETH': "**Ethereum Education:** Blockchain platform (2015) enabling smart contracts and decentralized applications (DApps). Powers DeFi, NFTs, and various crypto innovations. Uses proof-of-stake consensus since 2022.",
        
        'SOL': "**Solana Education:** High-speed blockchain focused on scalability and low fees. Popular for DeFi and NFT applications. Uses unique proof-of-history consensus mechanism for faster transaction processing."
    }
    
    return education_content.get(crypto, f"**{crypto} Education:** This cryptocurrency has specific use cases and technology. Please ask about particular aspects like consensus mechanism, use cases, or tokenomics for detailed information.")

def generate_medium_general_response(question: str, analysis: Dict[str, Any]) -> str:
    """Generate medium-length general response"""
    
    question_type = analysis["question_type"]
    
    if question_type == "trading_advice":
        return "**Trading Guidance:** Successful crypto trading requires risk management, technical analysis skills, and emotional discipline. Use stop-losses, position sizing, and never risk more than 2-3% per trade. Market timing is extremely difficult - consider long-term investing instead."
    
    elif question_type == "prediction":
        return "**Market Predictions:** Crypto markets are highly unpredictable due to volatility, regulatory factors, and sentiment swings. While technical analysis can provide insights, no one can accurately predict short-term price movements. Focus on long-term fundamentals instead."
    
    else:
        return "**Professional Crypto Analysis:** I can provide insights on cryptocurrency investments, technology, market analysis, and educational content. Please specify your area of interest for detailed information tailored to your needs."



def generate_investment_advice(question: str, crypto_mentions: list, sentiment: str) -> str:
    """Generate dynamic investment advice based on question context"""
    
    advice_parts = []
    
    # Analyze the specific investment question
    if "safe" in question.lower() or "risk" in question.lower():
        advice_parts.append("**🛡️ Crypto Investment Safety Reality:**\n")
        advice_parts.append("Crypto investing involves significant risks but can be part of a balanced portfolio. Here's what you need to know:\n\n")
        
        advice_parts.append("⚠️ Key Risks:\n")
        advice_parts.append("• Extreme volatility (50-90% price swings)\n")
        advice_parts.append("• Regulatory uncertainty in many countries\n") 
        advice_parts.append("• Technology risks and potential security breaches\n")
        advice_parts.append("• Market manipulation and liquidity issues\n\n")
        
        if sentiment == "fearful":
            advice_parts.append("🤝 For Cautious Investors:\n")
            advice_parts.append("• Start with just 1-5% of your portfolio\n")
            advice_parts.append("• Stick to Bitcoin and Ethereum initially\n")
            advice_parts.append("• Use dollar-cost averaging over 6-12 months\n")
            advice_parts.append("• Only invest money you can completely afford to lose\n")
        else:
            advice_parts.append("💰 Smart Investment Approach:\n")
            advice_parts.append("• 5-10% portfolio allocation for moderate risk tolerance\n")
            advice_parts.append("• 70% Bitcoin/Ethereum, 30% quality altcoins\n") 
            advice_parts.append("• Long-term holding strategy (3-5+ years)\n")
            advice_parts.append("• Regular rebalancing and profit-taking during peaks\n")
    
    elif "should i" in question.lower() or "worth it" in question.lower():
        advice_parts.append("**🤔 Should You Invest in Crypto? Here's My Analysis:**\n\n")
        
        advice_parts.append("✅ You SHOULD consider crypto if:\n")
        advice_parts.append("• You have emergency fund and stable income\n")
        advice_parts.append("• You can handle high volatility emotionally\n")
        advice_parts.append("• You're investing for 3+ years minimum\n")
        advice_parts.append("• You understand the technology basics\n")
        advice_parts.append("• You want portfolio diversification\n\n")
        
        advice_parts.append("❌ AVOID crypto investing if:\n")
        advice_parts.append("• You need the money within 2 years\n")
        advice_parts.append("• You're borrowing money to invest\n")
        advice_parts.append("• You panic during market downturns\n")
        advice_parts.append("• You don't understand what you're buying\n")
        advice_parts.append("• You're hoping to get rich quick\n")
    
    elif crypto_mentions:
        specific_crypto = crypto_mentions[0]
        advice_parts.append(f"**📊 {specific_crypto} Investment Analysis:**\n\n")
        
        if "BTC" in specific_crypto or "BITCOIN" in specific_crypto:
            advice_parts.append("**Bitcoin Investment Thesis:**\n")
            advice_parts.append("• Digital store of value with fixed supply (21M coins)\n")
            advice_parts.append("• Growing institutional adoption and ETF approval\n")
            advice_parts.append("• Lowest risk crypto investment option\n")
            advice_parts.append("• Good entry point for crypto beginners\n")
            advice_parts.append("• Historical 4-year cycles show strong long-term returns\n")
        
        elif "ETH" in specific_crypto or "ETHEREUM" in specific_crypto:
            advice_parts.append("**Ethereum Investment Thesis:**\n")
            advice_parts.append("• Leading smart contract platform powering DeFi/NFTs\n")
            advice_parts.append("• Generates yield through staking (4-6% APY)\n")
            advice_parts.append("• Deflationary tokenomics from fee burning\n")
            advice_parts.append("• Higher growth potential but more volatile than Bitcoin\n")
            advice_parts.append("• Essential infrastructure for decentralized applications\n")
        
        else:
            advice_parts.append(f"**{specific_crypto} Considerations:**\n")
            advice_parts.append("• Higher risk/reward compared to Bitcoin/Ethereum\n")
            advice_parts.append("• Research the project's fundamentals thoroughly\n")
            advice_parts.append("• Limit to 5-10% of total crypto allocation\n")
            advice_parts.append("• Understand the technology and use case\n")
            advice_parts.append("• Monitor development activity and partnerships\n")
    
    else:
        advice_parts.append("**💼 General Crypto Investment Strategy:**\n\n")
        advice_parts.append("• **Portfolio Allocation**: 5-10% of total investments\n")
        advice_parts.append("• **Diversification**: Mix of Bitcoin, Ethereum, and select altcoins\n")
        advice_parts.append("• **Strategy**: Dollar-cost averaging over time\n")
        advice_parts.append("• **Timeline**: Long-term holding (3-5+ years)\n")
        advice_parts.append("• **Security**: Use hardware wallet for large amounts\n")
    
    return "".join(advice_parts)

def generate_price_analysis(question: str, crypto_mentions: list, real_time_data: Dict[str, Any] = {}) -> str:
    """Generate dynamic price analysis with real-time data"""
    
    analysis_parts = []
    analysis_parts.append("**� Real-Time Crypto Price Analysis:**\n\n")
    
    # Show real-time price data if available
    if real_time_data.get("success") and real_time_data.get("data"):
        analysis_parts.append("**💰 Current Live Prices:**\n")
        
        crypto_name_map = {
            'bitcoin': 'Bitcoin (BTC)',
            'ethereum': 'Ethereum (ETH)', 
            'solana': 'Solana (SOL)',
            'cardano': 'Cardano (ADA)',
            'polygon': 'Polygon (MATIC)',
            'avalanche': 'Avalanche (AVAX)',
            'chainlink': 'Chainlink (LINK)'
        }
        
        for crypto_id, price_info in real_time_data["data"].items():
            crypto_name = crypto_name_map.get(crypto_id, crypto_id.title())
            price = price_info["price"]
            change_24h = price_info["price_change_24h"]
            market_cap = price_info["market_cap"]
            
            # Format price with appropriate decimals
            if price >= 1:
                price_str = f"${price:,.2f}"
            else:
                price_str = f"${price:.6f}"
                
            # Format change with color indicator
            if change_24h > 0:
                change_emoji = "📈"
                change_str = f"+{change_24h:.2f}%"
            else:
                change_emoji = "📉" 
                change_str = f"{change_24h:.2f}%"
                
            # Format market cap
            if market_cap > 1e12:
                cap_str = f"${market_cap/1e12:.2f}T"
            elif market_cap > 1e9:
                cap_str = f"${market_cap/1e9:.2f}B"
            elif market_cap > 1e6:
                cap_str = f"${market_cap/1e6:.2f}M"
            else:
                cap_str = f"${market_cap:,.0f}"
                
            analysis_parts.append(f"• **{crypto_name}**: {price_str} {change_emoji} {change_str} (24h)\n")
            analysis_parts.append(f"  Market Cap: {cap_str}\n\n")
        
        analysis_parts.append(f"*Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*\n\n")
    
    # Add intelligent analysis based on mentioned cryptos
    if crypto_mentions:
        crypto = crypto_mentions[0]
        analysis_parts.append(f"**🔍 {crypto} Analysis:**\n")
        
        if "BTC" in crypto or "BITCOIN" in crypto:
            analysis_parts.append("• **Digital Gold**: Store of value narrative strengthening\n")
            analysis_parts.append("• **Supply Dynamics**: Only ~1M BTC left to mine (94% mined)\n")
            analysis_parts.append("• **Institutional Adoption**: Major ETFs and corporate treasuries\n") 
            analysis_parts.append("• **Price Catalysts**: Regulatory clarity, sovereign adoption\n")
        
        elif "ETH" in crypto or "ETHEREUM" in crypto:
            analysis_parts.append("• **Smart Contract Leader**: Dominant DeFi and NFT ecosystem\n")
            analysis_parts.append("• **Technology Upgrades**: Proof-of-Stake, Layer 2 scaling\n")
            analysis_parts.append("• **Deflationary Mechanics**: EIP-1559 fee burning during high usage\n")
            analysis_parts.append("• **Institutional Interest**: Potential ETF approval pending\n")
        
        elif "SOL" in crypto or "SOLANA" in crypto:
            analysis_parts.append("• **High Performance**: Sub-second finality, low transaction costs\n")
            analysis_parts.append("• **Growing Ecosystem**: DeFi, NFTs, Web3 applications expanding\n")
            analysis_parts.append("• **Mobile Focus**: Saga phone and mobile-first approach\n")
            analysis_parts.append("• **Risk Factors**: Network stability concerns, centralization debates\n")
            
        else:
            analysis_parts.append(f"• **Market Position**: {crypto} performance correlates with Bitcoin trends\n")
            analysis_parts.append("• **Fundamental Analysis**: Research project roadmap and partnerships\n")
            analysis_parts.append("• **Higher Volatility**: Altcoins typically more volatile than BTC/ETH\n")
            analysis_parts.append("• **Due Diligence**: Monitor development activity and adoption metrics\n")
    else:
        analysis_parts.append("**🌐 General Market Overview:**\n")
        analysis_parts.append("• **Market Cycle**: Mid-cycle with growing institutional participation\n")
        analysis_parts.append("• **Regulatory Progress**: Clearer frameworks emerging globally\n")
        analysis_parts.append("• **Technology Maturation**: Infrastructure improving, user experience better\n")
        analysis_parts.append("• **Adoption Trends**: Mainstream integration accelerating\n")
    
    analysis_parts.append("\n**🎯 Key Price Factors to Monitor:**\n")
    analysis_parts.append("• **Institutional Flows**: ETF adoption and corporate treasury allocation\n")
    analysis_parts.append("• **Regulatory Developments**: Government policies and legal clarity\n")
    analysis_parts.append("• **Macroeconomic Conditions**: Interest rates, inflation, global liquidity\n")
    analysis_parts.append("• **Technology Progress**: Network upgrades, scalability solutions\n")
    
    analysis_parts.append("\n**📊 Investment Considerations:**\n")
    analysis_parts.append("• **Timing**: Dollar-cost averaging reduces volatility impact\n")
    analysis_parts.append("• **Diversification**: Don't put all funds in single cryptocurrency\n") 
    analysis_parts.append("• **Risk Management**: Only invest what you can afford to lose\n")
    analysis_parts.append("• **Long-term View**: Focus on adoption trends vs. short-term price movements\n")
    
    analysis_parts.append("\n*⚠️ This is not financial advice. Cryptocurrency prices are highly volatile and unpredictable.*")
    
    return "".join(analysis_parts)

def generate_educational_content(question: str, crypto_mentions: list) -> str:
    """Generate educational content based on question"""
    
    content_parts = []
    
    if "work" in question.lower() or "technology" in question.lower():
        content_parts.append("**🔧 How Cryptocurrency Technology Works:**\n\n")
        content_parts.append("**Blockchain Basics:**\n")
        content_parts.append("• Distributed ledger technology storing transaction records\n")
        content_parts.append("• Cryptographic security prevents tampering and fraud\n")
        content_parts.append("• Network consensus validates all transactions\n")
        content_parts.append("• Decentralized - no single point of control or failure\n\n")
        
        content_parts.append("**Key Innovations:**\n")
        content_parts.append("• **Bitcoin**: Digital money without banks or governments\n")
        content_parts.append("• **Ethereum**: Programmable blockchain for smart contracts\n")
        content_parts.append("• **DeFi**: Financial services without traditional intermediaries\n")
        content_parts.append("• **NFTs**: Unique digital ownership certificates\n")
        
    elif "what" in question.lower():
        if crypto_mentions:
            crypto = crypto_mentions[0]
            content_parts.append(f"**❓ What is {crypto}?**\n\n")
            
            if "BTC" in crypto or "BITCOIN" in crypto:
                content_parts.append("**Bitcoin Explained:**\n")
                content_parts.append("• First and largest cryptocurrency (digital gold)\n")
                content_parts.append("• Fixed supply of 21 million coins maximum\n")
                content_parts.append("• Peer-to-peer electronic cash system\n")
                content_parts.append("• Store of value and hedge against inflation\n")
                content_parts.append("• Secured by massive global mining network\n")
            
            elif "ETH" in crypto or "ETHEREUM" in crypto:
                content_parts.append("**Ethereum Explained:**\n")
                content_parts.append("• World computer enabling smart contracts and DApps\n")
                content_parts.append("• Platform for decentralized finance (DeFi)\n")
                content_parts.append("• Native currency (ETH) powers the network\n")
                content_parts.append("• Proof-of-stake consensus (environmentally friendly)\n")
                content_parts.append("• Foundation for NFTs, DAOs, and Web3 applications\n")
        else:
            content_parts.append("**🎓 Cryptocurrency Education:**\n\n")
            content_parts.append("Cryptocurrency is digital money secured by cryptography and powered by blockchain technology. Unlike traditional money, it operates without banks or governments controlling it.\n\n")
            content_parts.append("**Core Concepts:**\n")
            content_parts.append("• **Decentralization**: No single authority controls it\n")
            content_parts.append("• **Transparency**: All transactions are publicly visible\n")
            content_parts.append("• **Immutability**: Transaction history cannot be changed\n")
            content_parts.append("• **Programmability**: Smart contracts enable automated agreements\n")
    
    elif "how" in question.lower():
        content_parts.append("**📚 Getting Started with Crypto:**\n\n")
        content_parts.append("**Step 1: Education**\n")
        content_parts.append("• Learn basics: blockchain, wallets, exchanges, security\n")
        content_parts.append("• Understand risks: volatility, regulation, technology\n")
        content_parts.append("• Research specific projects and their use cases\n\n")
        
        content_parts.append("**Step 2: Setup**\n") 
        content_parts.append("• Choose reputable exchange (Coinbase, Kraken, Binance)\n")
        content_parts.append("• Complete identity verification process\n")
        content_parts.append("• Enable two-factor authentication for security\n\n")
        
        content_parts.append("**Step 3: Investment**\n")
        content_parts.append("• Start small with Bitcoin or Ethereum\n")
        content_parts.append("• Use dollar-cost averaging strategy\n")
        content_parts.append("• Consider hardware wallet for storage\n")
    
    return "".join(content_parts)

def generate_trading_advice(question: str, crypto_mentions: list) -> str:
    """Generate trading advice"""
    
    advice_parts = []
    advice_parts.append("**📊 Crypto Trading Guidance:**\n\n")
    
    if "when" in question.lower() or "timing" in question.lower():
        advice_parts.append("**⏰ Market Timing Strategy:**\n")
        advice_parts.append("• **Truth**: Timing the market consistently is nearly impossible\n")
        advice_parts.append("• **Better Approach**: Dollar-cost averaging over time\n")
        advice_parts.append("• **Buy Signals**: Fear in market, technical support levels\n")
        advice_parts.append("• **Sell Signals**: Euphoria peaks, technical resistance levels\n")
        advice_parts.append("• **Best Strategy**: Time in market beats timing the market\n\n")
    
    advice_parts.append("**🎯 Trading Fundamentals:**\n")
    advice_parts.append("• **Risk Management**: Never risk more than 2% per trade\n")
    advice_parts.append("• **Position Sizing**: Calculate based on stop loss distance\n")
    advice_parts.append("• **Stop Losses**: Always define your exit before entering\n")
    advice_parts.append("• **Profit Taking**: Scale out systematically (25%, 50%, 75%)\n")
    advice_parts.append("• **Emotional Control**: Stick to your plan regardless of emotions\n\n")
    
    advice_parts.append("**📈 Technical Analysis Basics:**\n")
    advice_parts.append("• **Support/Resistance**: Key price levels for entries/exits\n")
    advice_parts.append("• **Volume**: Confirms price movements and breakouts\n") 
    advice_parts.append("• **RSI**: Shows overbought (>70) and oversold (<30) conditions\n")
    advice_parts.append("• **Moving Averages**: Trend direction and momentum\n")
    advice_parts.append("• **Chart Patterns**: Triangles, flags, head and shoulders\n")
    
    return "".join(advice_parts)

def generate_prediction_analysis(question: str, crypto_mentions: list) -> str:
    """Generate prediction analysis"""
    
    pred_parts = []
    pred_parts.append("**🔮 Crypto Future Analysis:**\n\n")
    
    pred_parts.append("**⚠️ Prediction Disclaimer:**\n")
    pred_parts.append("No one can predict crypto prices with certainty. Here's how to think about the future:\n\n")
    
    pred_parts.append("**🔄 Market Cycle Perspective:**\n")
    pred_parts.append("• We're likely in mid-cycle of current crypto adoption phase\n")
    pred_parts.append("• Historical cycles last 3-4 years (bull → bear → bull)\n")
    pred_parts.append("• Each cycle reaches higher highs due to growing adoption\n")
    pred_parts.append("• Volatility decreases as market matures and grows\n\n")
    
    pred_parts.append("**📈 Long-term Drivers:**\n")
    pred_parts.append("• **Institutional Adoption**: More companies and funds entering\n")
    pred_parts.append("• **Regulatory Clarity**: Clearer rules enabling growth\n")
    pred_parts.append("• **Technology Improvements**: Scaling, security, usability\n")
    pred_parts.append("• **Global Adoption**: Emerging markets embracing crypto\n")
    pred_parts.append("• **Inflation Hedge**: Alternative to traditional assets\n\n")
    
    pred_parts.append("**🎯 Realistic Expectations:**\n")
    pred_parts.append("Focus on adoption trends rather than price predictions. Invest in projects solving real problems with strong fundamentals.")
    
    return "".join(pred_parts)

def generate_general_crypto_response(question: str, analysis: Dict[str, Any]) -> str:
    """Generate general crypto response for unmatched questions"""
    
    general_parts = []
    general_parts.append("**🤖 Crypto Analysis Assistant:**\n\n")
    
    # Analyze what the user might be asking about
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['recommend', 'suggest', 'advice', 'opinion']):
        general_parts.append("**💡 My Crypto Recommendations:**\n")
        general_parts.append("Based on your question, here's my guidance:\n\n")
        general_parts.append("• **For Beginners**: Start with Bitcoin and Ethereum only\n")
        general_parts.append("• **For Safety**: Use reputable exchanges and hardware wallets\n")
        general_parts.append("• **For Strategy**: Dollar-cost average over 6-12 months\n")
        general_parts.append("• **For Success**: Invest only what you can afford to lose\n")
        general_parts.append("• **For Learning**: Take time to understand before investing more\n")
    
    elif any(word in question_lower for word in ['help', 'confused', 'understand', 'explain']):
        general_parts.append("**🎓 Let me help clarify crypto for you:**\n\n")
        general_parts.append("Cryptocurrency can seem complex, but here are the essentials:\n\n")
        general_parts.append("• **Bitcoin**: Digital gold, store of value, limited supply\n")
        general_parts.append("• **Ethereum**: Smart contract platform, powers DeFi and NFTs\n")  
        general_parts.append("• **Investing**: High risk/high reward, only invest spare money\n")
        general_parts.append("• **Storage**: Use hardware wallets for security\n")
        general_parts.append("• **Strategy**: Long-term holding typically works better than trading\n")
    
    else:
        # Analyze the question content and provide relevant response
        general_parts.append("**📊 Analyzing your crypto question:**\n\n")
        
        if analysis["crypto_mentions"]:
            crypto_list = ", ".join(analysis["crypto_mentions"])
            general_parts.append(f"I see you're asking about: **{crypto_list}**\n\n")
        
        general_parts.append("**🎯 Key Points to Consider:**\n")
        general_parts.append("• **Research First**: Understand what you're investing in\n")
        general_parts.append("• **Risk Management**: Only invest money you can afford to lose\n")
        general_parts.append("• **Long-term View**: Crypto rewards patience over speculation\n")
        general_parts.append("• **Security**: Use proper wallets and security practices\n")
        general_parts.append("• **Diversification**: Don't put all money in one cryptocurrency\n")
        
        general_parts.append("\n**💬 For more specific help, try asking:**\n")
        general_parts.append("• \"Is Bitcoin safe to invest in?\"\n")
        general_parts.append("• \"How do I buy Ethereum?\"\n")
        general_parts.append("• \"What's the best crypto trading strategy?\"\n")
        general_parts.append("• \"Should I invest in [specific crypto]?\"\n")
    
    return "".join(general_parts)

# API Routes
@app.get("/")
async def root():
    return {
        "message": "🚀 Crypto Analytics AI Backend is running!",
        "ai_status": "online" if AI_SERVICE_AVAILABLE else "fallback",
        "docs": "/docs"
    }

@app.get("/test/connection")
async def test_connection():
    """Simple test endpoint to verify API connectivity"""
    return {
        "status": "success",
        "message": "API connection working",
        "timestamp": datetime.now().isoformat(),
        "port": 8000
    }

# Authentication Endpoints
@app.post("/api/auth/register", response_model=AuthResponse)
async def register_user(user: UserRegistration):
    """Register new user with MySQL database"""
    try:
        result = auth_system.register_user(
            name=user.name,
            username=user.username,
            email=user.email.lower().strip(),
            password=user.password
        )
        
        return AuthResponse(
            success=result["success"],
            message=result["message"]
        )
        
    except Exception as e:
        print(f"❌ Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )
@app.post("/api/auth/login", response_model=AuthResponse)
async def login_user(user: UserLogin):
    """Login user with MySQL database authentication"""
    try:
        result = auth_system.login_user(
            login_input=user.login,  # Can be username or email
            password=user.password
        )
        
        if result["success"]:
            return AuthResponse(
                success=True,
                message=result["message"],
                token=result["token"],
                user=result["user"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"]
            )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@app.post("/api/auth/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Logout current user by invalidating token"""
    try:
        # This would typically invalidate the token in the session store
        # For now, we'll just return success (frontend should remove token)
        return {
            "success": True,
            "message": "Logged out successfully"
        }
    except Exception as e:
        print(f"❌ Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during logout"
        )

@app.post("/verify-token")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify JWT token and return user information"""
    return {
        "success": True,
        "user": current_user
    }

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "success": True,
        "user": current_user
    }

@app.get("/api/auth/debug")
async def auth_debug():
    """Debug endpoint to check database connection"""
    try:
        # Test database connection
        if auth_system.db.connect():
            return {
                "database": "connected",
                "auth_system": "ready",
                "message": "Authentication system is working"
            }
        else:
            return {
                "database": "disconnected",
                "auth_system": "not ready",
                "message": "Database connection failed"
            }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Authentication debug failed"
        }

@app.get("/api/v1/ai/chat/health")
async def ai_health_check():
    return {
        "status": "healthy",
        "ai_service": "online" if AI_SERVICE_AVAILABLE else "fallback", 
        "message": "AI Chat service is running"
    }

@app.post("/api/v1/ai/chat", response_model=ChatResponse)
async def ai_chat(request: ChatMessage):
    """
    Main AI chat endpoint - Enhanced with ML predictions and comprehensive Groq AI
    
    This endpoint now integrates:
    - ML-powered price predictions
    - Real-time technical analysis
    - Comprehensive crypto knowledge via Groq AI
    - Intent detection and smart routing
    """
    try:
        user_message = request.message
        context = request.user_context or {}
        
        # Use the new ML-powered chatbot service
        try:
            from app.services.ai_chatbot import get_chatbot
            
            # Initialize chatbot with Groq API key
            bot = get_chatbot(groq_api_key=GROQ_API_KEY)
            
            # Get response from enhanced chatbot
            response = await bot.chat(user_message)
            
            if response.get('success'):
                # Map ML chatbot response to existing ChatResponse format
                suggestions = []
                intent = response.get('intent', 'general')
                
                # Generate smart suggestions based on intent
                if intent == 'prediction':
                    suggestions = ["Show analysis", "Compare with others", "Check technical indicators", "Historical trends"]
                elif intent == 'analysis':
                    suggestions = ["Price prediction", "Market sentiment", "Risk assessment", "Portfolio impact"]
                elif intent == 'price_inquiry':
                    suggestions = ["Predict future price", "Technical analysis", "Compare cryptocurrencies", "Market trends"]
                else:
                    suggestions = ["Predict prices", "Analyze crypto", "Compare coins", "Market insights"]
                
                return ChatResponse(
                    response=response['message'],
                    source=response.get('source', 'ml_chatbot'),
                    suggestions=suggestions
                )
            else:
                # Fallback if ML chatbot fails
                raise Exception(response.get('error', 'Unknown error'))
                
        except ImportError as e:
            print(f"⚠️ ML chatbot not available: {e}")
            # Fall through to old system
        except Exception as e:
            print(f"⚠️ ML chatbot error: {e}")
            # Fall through to old system
        
        # Fallback to original AI system if ML chatbot fails
        if AI_SERVICE_AVAILABLE:
            try:
                ai_response = await get_real_ai_response(user_message, context)
                return ChatResponse(
                    response=ai_response,
                    source="groq_ai",
                    suggestions=["Follow up", "More analysis", "Different perspective", "Technical details"]
                )
            except Exception as e:
                print(f"Real AI failed, using fallback: {e}")
        
        # Use enhanced fallback
        fallback_response = await get_enhanced_fallback_response(user_message, context)
        return ChatResponse(
            response=fallback_response,
            source="enhanced_fallback",
            suggestions=["Try again", "Bitcoin analysis", "Portfolio review", "Market trends"]
        )
        
    except Exception as e:
        print(f"Error in ai_chat: {e}")
        return ChatResponse(
            response=f"🚨 I'm experiencing technical difficulties: {str(e)}\n\nPlease try again in a moment.",
            source="error_fallback",
            suggestions=["Try again", "Check connection", "Restart service"]
        )

@app.post("/api/ai/chat", response_model=ChatResponse)
async def ai_chat_frontend(request: ChatMessage):
    """Frontend AI chat endpoint - this is what the frontend expects"""
    return await ai_chat(request)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_simplified(request: ChatMessage):
    """Simplified chat endpoint for frontend compatibility"""
    return await ai_chat(request)


# ============================================================================
# ML-POWERED AI CHATBOT ENDPOINTS (with ML Model Integration)
# ============================================================================

# Import ML chatbot service
try:
    from app.services.ai_chatbot import get_chatbot
    ML_CHATBOT_AVAILABLE = True
    print("✅ ML-powered chatbot service loaded")
except ImportError as e:
    ML_CHATBOT_AVAILABLE = False
    print(f"⚠️ ML chatbot service not available: {e}")


class MLChatMessage(BaseModel):
    """ML Chat message model"""
    message: str
    user_id: Optional[str] = None


class MLChatResponse(BaseModel):
    """ML Chat response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    intent: Optional[str] = None
    symbol: Optional[str] = None
    timestamp: str


@app.post("/api/ml/chat", response_model=MLChatResponse)
async def ml_chat(request: MLChatMessage):
    """
    Chat with ML-powered AI assistant
    
    This endpoint uses trained machine learning models for crypto predictions.
    
    Example messages:
    - "Predict Bitcoin price"
    - "Analyze Ethereum"
    - "What's the current price of BTC?"
    """
    if not ML_CHATBOT_AVAILABLE:
        return MLChatResponse(
            success=False,
            message="ML chatbot service is not available",
            timestamp=datetime.now().isoformat()
        )
    
    try:
        bot = get_chatbot(groq_api_key=GROQ_API_KEY)
        response = await bot.chat(request.message, request.user_id)
        return MLChatResponse(**response)
    except Exception as e:
        return MLChatResponse(
            success=False,
            message=f"Error: {str(e)}",
            timestamp=datetime.now().isoformat()
        )


@app.post("/api/ml/predict/{symbol}")
async def ml_predict(symbol: str, days_ahead: int = 7):
    """
    Get ML-based price prediction for a cryptocurrency
    
    Uses trained Random Forest/Gradient Boosting models.
    """
    if not ML_CHATBOT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="ML prediction service is not available"
        )
    
    try:
        bot = get_chatbot(groq_api_key=GROQ_API_KEY)
        message = f"Predict {symbol} price for {days_ahead} days"
        response = await bot.chat(message)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@app.get("/api/ml/model-info")
async def ml_model_info():
    """Get information about the loaded ML model"""
    if not ML_CHATBOT_AVAILABLE:
        return {
            "ml_available": False,
            "message": "ML service not available"
        }
    
    try:
        from app.services.ml_predictor import ml_predictor
        model_info = ml_predictor.get_model_info()
        return {
            "ml_available": True,
            "model_info": model_info
        }
    except Exception as e:
        return {
            "ml_available": False,
            "error": str(e)
        }


@app.get("/api/ml/supported-cryptos")
async def ml_supported_cryptos():
    """Get list of cryptocurrencies supported by ML predictions"""
    if not ML_CHATBOT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="ML service not available"
        )
    
    try:
        bot = get_chatbot(groq_api_key=GROQ_API_KEY)
        return {
            "success": True,
            "cryptos": bot.supported_cryptos,
            "count": len(bot.supported_cryptos)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )

# ============================================================================
# END ML-POWERED AI CHATBOT ENDPOINTS
# ============================================================================


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.get("/api/v1/crypto/global-metrics")
async def get_global_metrics():
    """Get global crypto market metrics"""
    return {
        "status": "success",
        "data": {
            "total_market_cap": 2500000000000,  # $2.5T
            "total_volume_24h": 85000000000,    # $85B
            "bitcoin_dominance": 52.3,
            "ethereum_dominance": 17.8,
            "active_cryptocurrencies": 9500,
            "market_cap_change_24h": 2.1,
            "fear_greed_index": 72,
            "fear_greed_classification": "Greed"
        }
    }

@app.get("/api/v1/crypto/top-cryptos")
async def get_top_cryptos():
    """Get top cryptocurrencies"""
    return {
        "status": "success", 
        "data": [
            {
                "id": "bitcoin",
                "symbol": "BTC",
                "name": "Bitcoin",
                "price": 98500,
                "market_cap": 1950000000000,
                "volume_24h": 28000000000,
                "price_change_24h": 2.3,
                "price_change_7d": 8.7
            },
            {
                "id": "ethereum", 
                "symbol": "ETH",
                "name": "Ethereum",
                "price": 3650,
                "market_cap": 440000000000,
                "volume_24h": 15000000000,
                "price_change_24h": 1.8,
                "price_change_7d": 12.4
            },
            {
                "id": "solana",
                "symbol": "SOL", 
                "name": "Solana",
                "price": 245,
                "market_cap": 115000000000,
                "volume_24h": 3200000000,
                "price_change_24h": 4.2,
                "price_change_7d": 18.6
            }
        ]
    }

@app.get("/api/v1/crypto/portfolio/summary")
async def get_portfolio_summary():
    """Get portfolio summary"""
    return {
        "status": "success",
        "data": {
            "total_value": 0,
            "total_change_24h": 0,
            "total_change_7d": 0,
            "assets_count": 0,
            "top_performer": None,
            "worst_performer": None
        }
    }

@app.get("/api/market/data")
async def get_market_data():
    """Get global market data in the format expected by frontend"""
    return {
        "status": "success",
        "data": {
            "active_cryptocurrencies": 9847,
            "total_cryptocurrencies": 24123,
            "active_market_pairs": 89756,
            "active_exchanges": 756,
            "total_exchanges": 1234,
            "eth_dominance": 17.8,
            "btc_dominance": 52.3,
            "eth_dominance_yesterday": 17.6,
            "btc_dominance_yesterday": 52.1,
            "eth_dominance_24h_percentage_change": 1.14,
            "btc_dominance_24h_percentage_change": 0.38,
            "defi_volume_24h": 12500000000,
            "defi_volume_24h_reported": 12600000000,
            "defi_market_cap": 85000000000,
            "defi_24h_percentage_change": 2.5,
            "stablecoin_volume_24h": 45000000000,
            "stablecoin_volume_24h_reported": 45200000000,
            "stablecoin_market_cap": 125000000000,
            "stablecoin_24h_percentage_change": 0.1,
            "derivatives_volume_24h": 156000000000,
            "derivatives_volume_24h_reported": 156500000000,
            "derivatives_24h_percentage_change": 3.2,
            "quote": {
                "USD": {
                    "total_market_cap": 2500000000000,
                    "total_volume_24h": 85000000000,
                    "total_volume_24h_reported": 85500000000,
                    "altcoin_volume_24h": 45000000000,
                    "altcoin_volume_24h_reported": 45200000000,
                    "altcoin_market_cap": 1200000000000,
                    "defi_volume_24h": 12500000000,
                    "defi_volume_24h_reported": 12600000000,
                    "defi_24h_percentage_change": 2.5,
                    "defi_market_cap": 85000000000,
                    "stablecoin_volume_24h": 45000000000,
                    "stablecoin_volume_24h_reported": 45200000000,
                    "stablecoin_24h_percentage_change": 0.1,
                    "stablecoin_market_cap": 125000000000,
                    "derivatives_volume_24h": 156000000000,
                    "derivatives_volume_24h_reported": 156500000000,
                    "derivatives_24h_percentage_change": 3.2,
                    "total_market_cap_yesterday": 2450000000000,
                    "total_volume_24h_yesterday": 83000000000,
                    "total_market_cap_yesterday_percentage_change": 2.04,
                    "total_volume_24h_yesterday_percentage_change": 2.41,
                    "last_updated": "2024-12-28T10:30:00.000Z"
                }
            }
        }
    }

# Resend OTP endpoint removed - now using direct MySQL authentication

# ===========================================
# PRODUCTION-READY API ENDPOINTS
# ===========================================

# Portfolio Management Models
class AssetCreate(BaseModel):
    symbol: str
    name: str
    amount: float
    avgBuyPrice: float
    source: str = "manual"

class AssetUpdate(BaseModel):
    amount: Optional[float] = None
    avgBuyPrice: Optional[float] = None

class PortfolioAsset(BaseModel):
    id: str
    symbol: str
    name: str
    amount: float
    avgBuyPrice: float
    currentPrice: float
    value: float
    change24h: float
    changePercent24h: float
    source: str

# Technical Analysis Models
class TechnicalIndicators(BaseModel):
    symbol: str
    rsi: Optional[float] = None
    macd: Optional[Dict[str, Any]] = None
    bb: Optional[Dict[str, Any]] = None  # Bollinger Bands
    sma: Optional[Dict[str, Any]] = None  # Simple Moving Average
    ema: Optional[Dict[str, Any]] = None  # Exponential Moving Average
    stoch: Optional[Dict[str, Any]] = None  # Stochastic Oscillator

class PriceHistoryRequest(BaseModel):
    symbol: str
    timeframe: str = "24h"
    limit: int = 100

class AlertCreate(BaseModel):
    symbol: str
    condition: str  # "above", "below", "change_percent"
    value: float
    message: str
    enabled: bool = True

class TradingSignal(BaseModel):
    id: str
    symbol: str
    type: str  # "BUY", "SELL", "HOLD"
    strength: int  # 1-100
    indicators: List[str]
    entry_price: float
    target_price: float
    stop_loss: float
    timeframe: str
    generated_at: datetime
    ai_confidence: int
    reason: str

# In-memory storage for demo (replace with database)
portfolio_assets = {}
user_alerts = {}
price_history_cache = {}

# ===========================================
# PORTFOLIO MANAGEMENT ENDPOINTS
# ===========================================

@app.post("/api/portfolio/assets")
async def add_portfolio_asset(asset: AssetCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Add asset to portfolio"""
    try:
        # Get current price from mock data
        current_price = random.uniform(100, 50000)  # Mock price
        change24h = random.uniform(-10, 10)
        
        asset_id = f"asset_{len(portfolio_assets) + 1}"
        new_asset = PortfolioAsset(
            id=asset_id,
            symbol=asset.symbol,
            name=asset.name,
            amount=asset.amount,
            avgBuyPrice=asset.avgBuyPrice,
            currentPrice=current_price,
            value=asset.amount * current_price,
            change24h=change24h,
            changePercent24h=change24h / current_price * 100,
            source=asset.source
        )
        
        portfolio_assets[asset_id] = new_asset.dict()
        
        return {
            "success": True,
            "message": "Asset added successfully",
            "asset": new_asset
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/portfolio/assets")
async def get_portfolio_assets(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all portfolio assets"""
    assets = list(portfolio_assets.values())
    total_value = sum(asset["value"] for asset in assets)
    total_change24h = sum(asset["change24h"] * asset["amount"] for asset in assets)
    
    return {
        "success": True,
        "assets": assets,
        "summary": {
            "totalValue": total_value,
            "totalChange24h": total_change24h,
            "totalChangePercent24h": (total_change24h / total_value * 100) if total_value > 0 else 0,
            "assetCount": len(assets)
        }
    }

@app.put("/api/portfolio/assets/{asset_id}")
async def update_portfolio_asset(asset_id: str, updates: AssetUpdate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update portfolio asset"""
    if asset_id not in portfolio_assets:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset = portfolio_assets[asset_id]
    if updates.amount is not None:
        asset["amount"] = updates.amount
        asset["value"] = updates.amount * asset["currentPrice"]
    
    if updates.avgBuyPrice is not None:
        asset["avgBuyPrice"] = updates.avgBuyPrice
    
    portfolio_assets[asset_id] = asset
    
    return {
        "success": True,
        "message": "Asset updated successfully",
        "asset": asset
    }

@app.delete("/api/portfolio/assets/{asset_id}")
async def delete_portfolio_asset(asset_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete portfolio asset"""
    if asset_id not in portfolio_assets:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    del portfolio_assets[asset_id]
    
    return {
        "success": True,
        "message": "Asset deleted successfully"
    }

@app.post("/api/portfolio/refresh-prices")
async def refresh_portfolio_prices(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh current prices for all portfolio assets"""
    try:
        for asset_id, asset in portfolio_assets.items():
            # Mock price update (replace with real API calls)
            new_price = asset["currentPrice"] * random.uniform(0.95, 1.05)
            change24h = (new_price - asset["currentPrice"]) / asset["currentPrice"] * 100
            
            asset["currentPrice"] = new_price
            asset["value"] = asset["amount"] * new_price
            asset["change24h"] = change24h
            asset["changePercent24h"] = change24h
        
        return {
            "success": True,
            "message": "Prices refreshed successfully",
            "updatedCount": len(portfolio_assets)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===========================================
# TECHNICAL ANALYSIS ENDPOINTS
# ===========================================

@app.get("/api/technical/indicators/{symbol}")
async def get_technical_indicators(symbol: str):
    """Get technical indicators for a cryptocurrency"""
    try:
        # Mock technical indicators (replace with real calculations)
        indicators = TechnicalIndicators(
            symbol=symbol,
            rsi=random.uniform(20, 80),
            macd={
                "macd": random.uniform(-50, 50),
                "signal": random.uniform(-50, 50),
                "histogram": random.uniform(-20, 20),
                "trend": random.choice(["bullish", "bearish", "neutral"])
            },
            bb={
                "upper": random.uniform(45000, 55000),
                "middle": random.uniform(40000, 50000),
                "lower": random.uniform(35000, 45000)
            },
            sma={
                "sma_20": random.uniform(38000, 48000),
                "sma_50": random.uniform(36000, 46000),
                "sma_200": random.uniform(30000, 40000)
            },
            ema={
                "ema_12": random.uniform(39000, 49000),
                "ema_26": random.uniform(37000, 47000)
            },
            stoch={
                "k_percent": random.uniform(0, 100),
                "d_percent": random.uniform(0, 100),
                "signal": random.choice(["overbought", "oversold", "neutral"])
            }
        )
        
        return {
            "success": True,
            "data": indicators
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/market/price-history")
async def get_price_history(request: PriceHistoryRequest):
    """Get price history for a cryptocurrency"""
    try:
        # Mock price history generation
        cache_key = f"{request.symbol}_{request.timeframe}"
        
        if cache_key not in price_history_cache:
            base_price = random.uniform(100, 50000)
            history = []
            
            for i in range(request.limit):
                price = base_price * (1 + random.uniform(-0.1, 0.1))
                volume = random.uniform(1000000, 100000000)
                
                history.append({
                    "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                    "price": price,
                    "volume": volume,
                    "high": price * 1.02,
                    "low": price * 0.98,
                    "open": price * random.uniform(0.99, 1.01),
                    "close": price
                })
                base_price = price
            
            price_history_cache[cache_key] = history[::-1]  # Reverse for chronological order
        
        return {
            "success": True,
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "data": price_history_cache[cache_key]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/search")
async def search_cryptocurrencies(q: str, limit: int = 10):
    """Search for cryptocurrencies"""
    # Mock search results
    mock_cryptos = [
        {"symbol": "BTC", "name": "Bitcoin", "price": 43250.50},
        {"symbol": "ETH", "name": "Ethereum", "price": 2650.30},
        {"symbol": "BNB", "name": "Binance Coin", "price": 315.20},
        {"symbol": "ADA", "name": "Cardano", "price": 0.48},
        {"symbol": "DOT", "name": "Polkadot", "price": 7.25},
        {"symbol": "LINK", "name": "Chainlink", "price": 14.80},
        {"symbol": "LTC", "name": "Litecoin", "price": 72.50},
        {"symbol": "BCH", "name": "Bitcoin Cash", "price": 243.60},
        {"symbol": "XLM", "name": "Stellar", "price": 0.12},
        {"symbol": "UNI", "name": "Uniswap", "price": 6.45}
    ]
    
    # Filter based on query
    filtered = [
        crypto for crypto in mock_cryptos 
        if q.lower() in crypto["name"].lower() or q.lower() in crypto["symbol"].lower()
    ][:limit]
    
    return {
        "success": True,
        "query": q,
        "results": filtered
    }

# ===========================================
# MARKET SENTIMENT ENDPOINTS
# ===========================================

@app.get("/api/market/sentiment")
async def get_market_sentiment():
    """Get overall market sentiment analysis"""
    try:
        sentiment_data = {
            "overall_score": random.uniform(0.3, 0.8),
            "sentiment_label": random.choice(["Bullish", "Bearish", "Neutral", "Very Bullish"]),
            "fear_greed_index": random.randint(10, 90),
            "social_mentions": {
                "bitcoin": random.randint(5000, 15000),
                "ethereum": random.randint(3000, 10000),
                "trending_coins": ["BTC", "ETH", "BNB", "ADA"]
            },
            "news_sentiment": {
                "positive": random.randint(40, 70),
                "neutral": random.randint(20, 40),
                "negative": random.randint(10, 30)
            },
            "last_updated": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": sentiment_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===========================================
# ALERTS MANAGEMENT ENDPOINTS
# ===========================================

@app.post("/api/alerts")
async def create_alert(alert: AlertCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new price alert"""
    try:
        alert_id = f"alert_{len(user_alerts) + 1}"
        new_alert = {
            "id": alert_id,
            "symbol": alert.symbol,
            "condition": alert.condition,
            "value": alert.value,
            "message": alert.message,
            "enabled": alert.enabled,
            "created_at": datetime.now().isoformat(),
            "triggered": False
        }
        
        user_alerts[alert_id] = new_alert
        
        return {
            "success": True,
            "message": "Alert created successfully",
            "alert": new_alert
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/alerts")
async def get_user_alerts(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all user alerts"""
    return {
        "success": True,
        "alerts": list(user_alerts.values())
    }

@app.delete("/api/alerts/{alert_id}")
async def delete_alert(alert_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete an alert"""
    if alert_id not in user_alerts:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    del user_alerts[alert_id]
    
    return {
        "success": True,
        "message": "Alert deleted successfully"
    }

# ===========================================
# TRADING SIGNALS ENDPOINTS
# ===========================================

@app.get("/api/trading/signals")
async def get_trading_signals(timeframe: str = "1h", limit: int = 10):
    """Get AI-generated trading signals"""
    try:
        signals = []
        popular_symbols = ["BTC", "ETH", "BNB", "ADA", "DOT", "LINK", "LTC", "BCH", "XLM", "UNI"]
        
        for i, symbol in enumerate(popular_symbols[:limit]):
            signal_type = random.choice(["BUY", "SELL", "HOLD"])
            strength = random.randint(60, 95)
            base_price = random.uniform(100, 50000)
            
            signal = TradingSignal(
                id=f"signal_{i+1}",
                symbol=symbol,
                type=signal_type,
                strength=strength,
                indicators=random.sample([
                    "RSI Oversold", "MACD Bullish", "Volume Breakout", 
                    "Support Bounce", "MA Golden Cross", "Breakout Pattern"
                ], 3),
                entry_price=base_price,
                target_price=base_price * (1.08 if signal_type == "BUY" else 0.95),
                stop_loss=base_price * (0.95 if signal_type == "BUY" else 1.03),
                timeframe=timeframe,
                generated_at=datetime.now(),
                ai_confidence=random.randint(75, 95),
                reason=f"Strong {signal_type.lower()} signal based on technical analysis"
            )
            
            signals.append(signal)
        
        return {
            "success": True,
            "timeframe": timeframe,
            "signals": [signal.dict() for signal in signals],
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===========================================
# NEWS AND ANALYTICS ENDPOINTS
# ===========================================

@app.get("/api/news")
async def get_crypto_news(limit: int = 20, hours_back: int = 24):
    """Get latest cryptocurrency news with sentiment analysis"""
    try:
        # Fetch news articles
        articles = await news_client.get_crypto_news(limit, hours_back)
        
        # Analyze market sentiment
        market_sentiment = sentiment_analyzer.analyze_market_sentiment(articles)
        
        return {
            "success": True,
            "articles": articles,
            "total_count": len(articles),
            "market_sentiment": market_sentiment,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/sentiment/{coin}")
async def get_coin_sentiment(coin: str, limit: int = 50):
    """Get sentiment analysis for a specific cryptocurrency"""
    try:
        # Fetch recent news
        articles = await news_client.get_crypto_news(limit, hours_back=48)
        
        # Get coin-specific sentiment
        coin_sentiment = sentiment_analyzer.get_coin_specific_sentiment(articles, coin)
        
        # Get relevant articles for this coin
        relevant_articles = [
            article for article in articles 
            if coin.lower() in article.get('mentioned_cryptos', [])
        ]
        
        return {
            "success": True,
            "coin": coin,
            "sentiment_analysis": coin_sentiment,
            "relevant_articles": relevant_articles[:10],  # Limit to 10 most relevant
            "total_relevant_articles": len(relevant_articles)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-sentiment")
async def get_overall_market_sentiment():
    """Get overall cryptocurrency market sentiment from news"""
    try:
        # Fetch comprehensive news data
        articles = await news_client.get_crypto_news(100, hours_back=72)
        
        # Analyze overall market sentiment
        market_sentiment = sentiment_analyzer.analyze_market_sentiment(articles)
        
        # Get sentiment for major cryptocurrencies
        major_coins = ['bitcoin', 'ethereum', 'cardano', 'solana', 'dogecoin']
        coin_sentiments = {}
        
        for coin in major_coins:
            coin_sentiment = sentiment_analyzer.get_coin_specific_sentiment(articles, coin)
            coin_sentiments[coin] = coin_sentiment
        
        return {
            "success": True,
            "overall_market_sentiment": market_sentiment,
            "individual_coin_sentiments": coin_sentiments,
            "analysis_period_hours": 72,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===========================================
# TECHNICAL INDICATORS ENDPOINTS
# ===========================================

@app.get("/api/technical-indicators/{coin_id}")
async def get_technical_indicators(
    coin_id: str, 
    days: int = 30,
    include_signals: bool = True
):
    """Get technical indicators analysis for a cryptocurrency"""
    try:
        # Try to fetch real data first
        try:
            data_fetcher = CryptoDataFetcher()
            price_data = await data_fetcher.get_price_history(coin_id, days)
            
            if price_data.get('success'):
                # Calculate technical indicators with real data
                ohlc_data = price_data['data']
                analysis = analyze_technical_indicators(ohlc_data)
            else:
                raise Exception("Failed to fetch real data")
                
        except Exception as real_data_error:
            print(f"⚠️ Using mock data for {coin_id}: {real_data_error}")
            # Fallback to mock data for demonstration
            analysis = get_mock_technical_indicators(coin_id)
        
        # Add metadata
        analysis['coin_id'] = coin_id
        analysis['period_days'] = days
        analysis['last_updated'] = datetime.now().isoformat()
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error in technical indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_mock_technical_indicators(coin_id: str) -> dict:
    """Generate mock technical indicators for demonstration"""
    import random
    
    # Mock price data based on coin
    base_prices = {
        'bitcoin': 45000,
        'ethereum': 3200,
        'binancecoin': 320,
        'cardano': 0.48,
        'solana': 98
    }
    
    base_price = base_prices.get(coin_id, 1000)
    current_price = base_price * (0.95 + random.random() * 0.1)  # ±5% variation
    
    return {
        'current_price': current_price,
        'price_change_24h': random.uniform(-5, 5),
        'volume': random.uniform(1000000, 50000000),
        'market_cap': current_price * random.uniform(19000000, 21000000),
        'technical_indicators': {
            'rsi': random.uniform(30, 70),
            'macd': {
                'macd': random.uniform(-100, 100),
                'signal': random.uniform(-80, 80),
                'histogram': random.uniform(-50, 50)
            },
            'bollinger_bands': {
                'upper': current_price * 1.02,
                'middle': current_price,
                'lower': current_price * 0.98
            },
            'sma_20': current_price * random.uniform(0.98, 1.02),
            'sma_50': current_price * random.uniform(0.95, 1.05),
            'ema_12': current_price * random.uniform(0.99, 1.01),
            'ema_26': current_price * random.uniform(0.97, 1.03),
            'stochastic': {
                'k': random.uniform(20, 80)
            },
            'williams_r': random.uniform(-80, -20),
            'atr': random.uniform(50, 200)
        },
        'trading_signals': [
            {
                'indicator': 'RSI',
                'signal': random.choice(['BUY', 'SELL', 'HOLD']),
                'reason': 'RSI indicates oversold/overbought conditions'
            },
            {
                'indicator': 'MACD',
                'signal': random.choice(['BUY', 'SELL', 'HOLD']),
                'reason': 'MACD crossover detected'
            },
            {
                'indicator': 'Bollinger Bands',
                'signal': random.choice(['BUY', 'SELL', 'HOLD']),
                'reason': 'Price near support/resistance level'
            }
        ],
        'analysis': f"Technical analysis for {coin_id.title()}: The current market conditions show mixed signals. RSI indicates moderate momentum, while MACD suggests potential trend changes. Consider the overall market sentiment before making trading decisions."
    }

@app.post("/api/technical-indicators/batch")
async def get_batch_technical_indicators(request: Dict[str, Any]):
    """Get technical indicators for multiple cryptocurrencies"""
    try:
        coin_ids = request.get('coin_ids', [])
        days = request.get('days', 30)
        
        if not coin_ids:
            raise HTTPException(status_code=400, detail="coin_ids list is required")
        
        # Fetch data for multiple coins
        data_fetcher = CryptoDataFetcher()
        batch_data = await data_fetcher.get_multiple_coins_data(coin_ids, days)
        
        results = {}
        for coin_id, ohlc_data in batch_data.items():
            if ohlc_data:
                analysis = analyze_technical_indicators(ohlc_data)
                analysis['coin_id'] = coin_id
                analysis['last_updated'] = datetime.now().isoformat()
                results[coin_id] = analysis
            else:
                results[coin_id] = {"error": "Failed to fetch data"}
        
        return {
            "success": True,
            "data": results,
            "processed_coins": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trading-signals/{coin_id}")
async def get_trading_signals(coin_id: str, timeframe: str = "1d"):
    """Get AI-powered trading signals for a cryptocurrency"""
    try:
        # Fetch recent price data
        data_fetcher = CryptoDataFetcher()
        days = 30 if timeframe == "1d" else 7
        price_data = await data_fetcher.get_price_history(coin_id, days)
        
        if not price_data.get('success'):
            raise HTTPException(status_code=400, detail="Failed to fetch price data")
        
        # Analyze technical indicators
        ohlc_data = price_data['data']
        analysis = analyze_technical_indicators(ohlc_data)
        
        # Extract signals
        signals = analysis.get('signals', {})
        
        # Enhance with AI insights
        if AI_SERVICE_AVAILABLE:
            try:
                ai_context = f"""
                Analyzing {coin_id.upper()} trading signals:
                - RSI: {analysis.get('rsi', [])[-1:]}
                - Overall Sentiment: {signals.get('overall_sentiment', 'neutral')}
                - Recent Recommendations: {len(signals.get('recommendations', []))}
                """
                
                ai_response = await get_real_ai_response(
                    f"Provide trading advice for {coin_id} based on technical analysis",
                    {"technical_data": ai_context}
                )
                signals['ai_insight'] = ai_response
            except Exception as ai_error:
                signals['ai_insight'] = "AI analysis temporarily unavailable"
        
        return {
            "success": True,
            "coin_id": coin_id,
            "timeframe": timeframe,
            "signals": signals,
            "technical_summary": {
                "rsi_current": analysis.get('rsi', [])[-1:],
                "trend": signals.get('overall_sentiment', 'neutral'),
                "strength": signals.get('strength', 0)
            },
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===========================================
# PORTFOLIO MANAGEMENT ENDPOINTS (Enhanced)
# ===========================================

@app.post("/api/portfolio/analyze")
async def analyze_portfolio_performance(request: Dict[str, Any]):
    """Analyze portfolio performance with technical indicators"""
    try:
        holdings = request.get('holdings', [])
        
        if not holdings:
            raise HTTPException(status_code=400, detail="Holdings data is required")
        
        portfolio_analysis = {
            "total_value": 0,
            "total_change_24h": 0,
            "coin_analysis": {},
            "overall_signals": {
                "bullish_count": 0,
                "bearish_count": 0,
                "neutral_count": 0
            }
        }
        
        data_fetcher = CryptoDataFetcher()
        
        for holding in holdings:
            coin_id = holding.get('coin_id', '').lower()
            amount = holding.get('amount', 0)
            
            if coin_id and amount > 0:
                # Get price data and technical analysis
                price_data = await data_fetcher.get_price_history(coin_id, 30)
                
                if price_data.get('success'):
                    ohlc_data = price_data['data']
                    current_price = ohlc_data[-1]['close'] if ohlc_data else 0
                    
                    # Calculate position value
                    position_value = amount * current_price
                    portfolio_analysis['total_value'] += position_value
                    
                    # Technical analysis
                    analysis = analyze_technical_indicators(ohlc_data)
                    signals = analysis.get('signals', {})
                    
                    # Count signals
                    sentiment = signals.get('overall_sentiment', 'neutral')
                    if sentiment == 'bullish':
                        portfolio_analysis['overall_signals']['bullish_count'] += 1
                    elif sentiment == 'bearish':
                        portfolio_analysis['overall_signals']['bearish_count'] += 1
                    else:
                        portfolio_analysis['overall_signals']['neutral_count'] += 1
                    
                    portfolio_analysis['coin_analysis'][coin_id] = {
                        "current_price": current_price,
                        "position_value": position_value,
                        "amount": amount,
                        "signals": signals,
                        "key_indicators": {
                            "rsi": analysis.get('rsi', [])[-1:],
                            "trend": sentiment
                        }
                    }
        
        # Overall portfolio sentiment
        signals = portfolio_analysis['overall_signals']
        if signals['bullish_count'] > signals['bearish_count']:
            portfolio_sentiment = "bullish"
        elif signals['bearish_count'] > signals['bullish_count']:
            portfolio_sentiment = "bearish"
        else:
            portfolio_sentiment = "neutral"
        
        portfolio_analysis['portfolio_sentiment'] = portfolio_sentiment
        portfolio_analysis['analysis_timestamp'] = datetime.now().isoformat()
        
        return {
            "success": True,
            "data": portfolio_analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===========================================
# WEBSOCKET ENDPOINTS FOR REAL-TIME DATA
# ===========================================

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time data streaming"""
    client = await websocket_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "subscribe":
                subscription_type = SubscriptionType(message.get("subscription_type"))
                coins = message.get("coins", [])
                await websocket_manager.subscribe_client(client, subscription_type, coins)
            
            elif message_type == "unsubscribe":
                subscription_type = SubscriptionType(message.get("subscription_type"))
                await websocket_manager.unsubscribe_client(client, subscription_type)
            
            elif message_type == "ping":
                await websocket_manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
            
            elif message_type == "get_current_prices":
                coins = message.get("coins", [])
                current_prices = {}
                for coin in coins:
                    if coin in websocket_manager.price_cache:
                        current_prices[coin] = websocket_manager.price_cache[coin]
                
                await websocket_manager.send_personal_message({
                    "type": "current_prices",
                    "data": current_prices,
                    "timestamp": datetime.now().isoformat()
                }, websocket)
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(client)
    except Exception as e:
        print(f"WebSocket error for client {client_id}: {e}")
        websocket_manager.disconnect(client)

# ===========================================
# ALERT SYSTEM ENDPOINTS
# ===========================================

# In-memory alert storage (replace with database in production)
user_alerts = {}  # {user_id: [alerts]}
active_alert_monitors = {}  # {alert_id: monitor_task}

async def monitor_price_alerts():
    """Global background task to monitor all active price alerts"""
    while True:
        try:
            # This is a placeholder for global alert monitoring
            # In a production environment, this would query the database for active alerts
            await asyncio.sleep(60)  # Check every minute
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in global alert monitor: {e}")
            await asyncio.sleep(60)

class PriceAlert(BaseModel):
    coin_id: str
    condition: str  # "above", "below", "change_up", "change_down"
    target_value: float
    notification_type: str = "websocket"  # "websocket", "email", "both"
    is_active: bool = True

@app.post("/api/alerts/create")
async def create_price_alert(alert: PriceAlert, user_id: str = "default_user"):
    """Create a new price alert"""
    try:
        alert_id = f"alert_{hash(f'{user_id}_{alert.coin_id}_{alert.target_value}')}"
        
        alert_data = {
            "id": alert_id,
            "user_id": user_id,
            "coin_id": alert.coin_id,
            "condition": alert.condition,
            "target_value": alert.target_value,
            "notification_type": alert.notification_type,
            "is_active": alert.is_active,
            "created_at": datetime.now().isoformat(),
            "triggered": False
        }
        
        # Store alert
        if user_id not in user_alerts:
            user_alerts[user_id] = []
        user_alerts[user_id].append(alert_data)
        
        # Start monitoring task
        monitor_task = asyncio.create_task(monitor_price_alert(alert_data))
        active_alert_monitors[alert_id] = monitor_task
        
        return {
            "success": True,
            "alert_id": alert_id,
            "message": "Price alert created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts/{user_id}")
async def get_user_alerts(user_id: str):
    """Get all alerts for a user"""
    try:
        alerts = user_alerts.get(user_id, [])
        return {
            "success": True,
            "alerts": alerts,
            "total_count": len(alerts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete a price alert"""
    try:
        # Cancel monitoring task
        if alert_id in active_alert_monitors:
            active_alert_monitors[alert_id].cancel()
            del active_alert_monitors[alert_id]
        
        # Remove from user alerts
        for user_id, alerts in user_alerts.items():
            user_alerts[user_id] = [a for a in alerts if a["id"] != alert_id]
        
        return {
            "success": True,
            "message": "Alert deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def monitor_price_alert(alert_data: Dict[str, Any]):
    """Background task to monitor price alerts"""
    alert_id = alert_data["id"]
    coin_id = alert_data["coin_id"]
    condition = alert_data["condition"]
    target_value = alert_data["target_value"]
    user_id = alert_data["user_id"]
    
    try:
        while alert_data.get("is_active", True) and not alert_data.get("triggered", False):
            # Fetch current price
            current_price_data = await websocket_manager._fetch_price_data(coin_id)
            
            if current_price_data:
                current_price = current_price_data["price"]
                price_change_24h = current_price_data.get("price_change_24h", 0)
                
                triggered = False
                
                if condition == "above" and current_price >= target_value:
                    triggered = True
                elif condition == "below" and current_price <= target_value:
                    triggered = True
                elif condition == "change_up" and price_change_24h >= target_value:
                    triggered = True
                elif condition == "change_down" and price_change_24h <= -target_value:
                    triggered = True
                
                if triggered:
                    # Mark alert as triggered
                    alert_data["triggered"] = True
                    alert_data["triggered_at"] = datetime.now().isoformat()
                    alert_data["triggered_price"] = current_price
                    
                    # Send notification
                    alert_notification = {
                        "alert_id": alert_id,
                        "coin_id": coin_id,
                        "condition": condition,
                        "target_value": target_value,
                        "current_price": current_price,
                        "message": f"{coin_id.upper()} {condition} {target_value} - Current price: {current_price}"
                    }
                    
                    # Send via WebSocket
                    await websocket_manager.send_alert(user_id, alert_notification)
                    
                    # Send email if configured
                    if alert_data.get("notification_type") in ["email", "both"]:
                        # Email notification would go here
                        pass
                    
                    break
            
            # Check every 30 seconds
            await asyncio.sleep(30)
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error monitoring alert {alert_id}: {e}")
    finally:
        # Clean up
        if alert_id in active_alert_monitors:
            del active_alert_monitors[alert_id]

if __name__ == "__main__":
    print("🚀 Starting Crypto Analytics AI Backend...")
    print(f"📊 AI Service: {'✅ Online (Groq)' if AI_SERVICE_AVAILABLE else '⚠️ Fallback Mode'}")
    
    # Force to use port 8000 only
    port = 8000
    try:
        print(f"🌐 Starting server on http://localhost:{port}")
        print(f"📖 API docs will be available at http://localhost:{port}/docs")
        print("💡 If port 8000 is in use, please stop other services using this port")
        
        uvicorn.run(app, host="127.0.0.1", port=port, reload=False)
    except OSError as e:
        if "WinError 10013" in str(e) or "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use!")
            print("💡 Please stop the service using port 8000 and try again")
            print("💡 You can check what's using port 8000 with: netstat -ano | findstr :8000")
            input("Press Enter to exit...")
        else:
            print(f"❌ Error starting server on port {port}: {e}")
            input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Unexpected error on port {port}: {e}")
        input("Press Enter to exit...")
