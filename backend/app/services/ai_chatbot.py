"""
AI Chatbot Service with ML Model Integration
Provides intelligent cryptocurrency analysis and predictions using trained ML models
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import re
import asyncio
import aiohttp
import pandas as pd

# Import ML predictor
try:
    from .ml_predictor import ml_predictor
    ML_AVAILABLE = True
except ImportError:
    print("⚠️ ML predictor not available")
    ML_AVAILABLE = False

# Import Groq if available for advanced NLP
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    print("⚠️ Groq not available, using rule-based responses")
    GROQ_AVAILABLE = False


class CryptoAIChatbot:
    """
    AI Chatbot for cryptocurrency analysis and predictions
    Integrates ML models for intelligent responses
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """Initialize AI chatbot"""
        self.groq_client = None
        self.ml_available = ML_AVAILABLE
        self.groq_available = GROQ_AVAILABLE and groq_api_key
        
        if self.groq_available:
            try:
                self.groq_client = Groq(api_key=groq_api_key)
                print("✅ Groq AI initialized for chatbot")
            except Exception as e:
                print(f"⚠️ Could not initialize Groq: {e}")
                self.groq_available = False
        
        # Supported crypto symbols
        self.supported_cryptos = [
            "BTC", "ETH", "USDT", "BNB", "XRP", "USDC", "ADA", "SOL", 
            "DOGE", "TRX", "DOT", "MATIC", "LTC", "SHIB", "AVAX"
        ]
        
        # Chat context/history
        self.chat_history = []
    
    @staticmethod
    def remove_bold_formatting(text: str) -> str:
        """Remove ** bold markdown formatting from text"""
        return text.replace('**', '')
    
    async def fetch_crypto_data(self, symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
        """
        Fetch historical crypto data for analysis
        
        Args:
            symbol: Crypto symbol (e.g., 'BTC')
            days: Number of days of historical data
            
        Returns:
            DataFrame with historical price data
        """
        try:
            # For demo purposes, we'll use CoinGecko API (free, no key required)
            coin_id_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'USDT': 'tether',
                'BNB': 'binancecoin',
                'XRP': 'ripple',
                'ADA': 'cardano',
                'SOL': 'solana',
                'DOGE': 'dogecoin',
                'DOT': 'polkadot',
                'MATIC': 'matic-network',
                'LTC': 'litecoin',
            }
            
            coin_id = coin_id_map.get(symbol.upper(), symbol.lower())
            
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Convert to DataFrame
                        prices = data.get('prices', [])
                        volumes = data.get('total_volumes', [])
                        
                        df = pd.DataFrame(prices, columns=['timestamp', 'close'])
                        df['volume'] = [v[1] for v in volumes]
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        
                        return df
                    else:
                        print(f"⚠️ Failed to fetch data: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ Error fetching crypto data: {e}")
            return None
    
    def extract_crypto_symbol(self, message: str) -> Optional[str]:
        """
        Extract cryptocurrency symbol from user message
        
        Args:
            message: User's message
            
        Returns:
            Crypto symbol or None
        """
        message_upper = message.upper()
        
        # Check for direct symbol mentions
        for symbol in self.supported_cryptos:
            if symbol in message_upper or symbol.lower() in message.lower():
                return symbol
        
        # Check for common names
        crypto_names = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH',
            'ripple': 'XRP',
            'cardano': 'ADA',
            'solana': 'SOL',
            'dogecoin': 'DOGE',
            'polkadot': 'DOT',
            'polygon': 'MATIC',
            'litecoin': 'LTC',
            'binance': 'BNB'
        }
        
        for name, symbol in crypto_names.items():
            if name in message.lower():
                return symbol
        
        return None
    
    def detect_intent(self, message: str) -> str:
        """
        Detect user's intent from message
        
        Args:
            message: User's message
            
        Returns:
            Intent type
        """
        message_lower = message.lower()
        
        # Prediction intent
        if any(word in message_lower for word in ['predict', 'forecast', 'future', 'will', 'expect', 'price target']):
            return 'prediction'
        
        # Analysis intent
        if any(word in message_lower for word in ['analyze', 'analysis', 'technical', 'indicators', 'trend']):
            return 'analysis'
        
        # Comparison intent
        if any(word in message_lower for word in ['compare', 'vs', 'versus', 'better', 'difference']):
            return 'comparison'
        
        # Price inquiry
        if any(word in message_lower for word in ['price', 'cost', 'worth', 'value']):
            return 'price_inquiry'
        
        # General info
        if any(word in message_lower for word in ['what is', 'tell me about', 'explain', 'info']):
            return 'general_info'
        
        return 'general'
    
    async def generate_ml_prediction(self, symbol: str) -> Dict:
        """
        Generate ML-based prediction for cryptocurrency
        
        Args:
            symbol: Crypto symbol
            
        Returns:
            Prediction result
        """
        try:
            if not self.ml_available:
                return {
                    'success': False,
                    'error': 'ML model not available'
                }
            
            # Fetch historical data
            crypto_data = await self.fetch_crypto_data(symbol, days=90)
            
            if crypto_data is None:
                return {
                    'success': False,
                    'error': 'Could not fetch crypto data'
                }
            
            # Make prediction using ML model
            prediction = ml_predictor.predict_price(symbol, crypto_data, days_ahead=7)
            
            return prediction
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def chat(self, message: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process user message and generate intelligent response
        
        Args:
            message: User's message
            user_id: Optional user identifier
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Add to chat history
            self.chat_history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
            
            # Extract crypto symbol
            symbol = self.extract_crypto_symbol(message)
            
            # Detect intent
            intent = self.detect_intent(message)
            
            # Generate response based on intent
            if intent == 'prediction' and symbol:
                response = await self._handle_prediction(symbol, message)
            elif intent == 'analysis' and symbol:
                response = await self._handle_analysis(symbol, message)
            elif intent == 'price_inquiry' and symbol:
                response = await self._handle_price_inquiry(symbol, message)
            elif intent == 'general_info' and symbol:
                response = await self._handle_general_info(symbol, message)
            else:
                response = await self._handle_general_query(message)
            
            # Add to chat history
            self.chat_history.append({
                'role': 'assistant',
                'content': response['message'],
                'timestamp': datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Sorry, I encountered an error: {str(e)}",
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _handle_prediction(self, symbol: str, message: str) -> Dict:
        """Handle prediction requests"""
        # Generate ML prediction
        prediction = await self.generate_ml_prediction(symbol)
        
        if not prediction.get('success'):
            return {
                'success': False,
                'message': f"Sorry, I couldn't generate a prediction for {symbol} right now. {prediction.get('error', '')}",
                'data': None,
                'timestamp': datetime.now().isoformat()
            }
        
        # Format response
        current_price = prediction['current_price']
        predicted_price = prediction['predicted_price']
        change_pct = prediction['price_change_pct']
        trend = prediction['trend']
        confidence = prediction['confidence']
        
        message_text = f"""📊 {symbol} Price Prediction (7-day forecast)

💰 Current Price: ${current_price:,.2f}
🎯 Predicted Price: ${predicted_price:,.2f}
📈 Expected Change: {change_pct:+.2f}%
📉 Trend: {trend.upper()}
🎲 Confidence: {confidence:.1f}%

Analysis:
Based on our machine learning model analyzing historical patterns, {symbol} is showing a {trend} trend. 
The model predicts a price of ${predicted_price:,.2f} in the next 7 days, representing a {abs(change_pct):.2f}% {'increase' if change_pct > 0 else 'decrease'}.

Recommendation: 
{'🟢 Consider buying opportunities if the trend continues.' if trend == 'bullish' else '🔴 Exercise caution and consider risk management.' if trend == 'bearish' else '🟡 Monitor the market for clearer signals.'}

Note: This is an AI-generated prediction and should not be considered financial advice.
"""
        
        return {
            'success': True,
            'message': message_text,
            'data': prediction,
            'intent': 'prediction',
            'symbol': symbol,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _handle_analysis(self, symbol: str, message: str) -> Dict:
        """Handle technical analysis requests"""
        crypto_data = await self.fetch_crypto_data(symbol, days=30)
        
        if crypto_data is None:
            return {
                'success': False,
                'message': f"Sorry, I couldn't fetch data for {symbol} analysis.",
                'timestamp': datetime.now().isoformat()
            }
        
        # Calculate basic technical indicators
        current_price = crypto_data['close'].iloc[-1]
        ma_7 = crypto_data['close'].rolling(window=7).mean().iloc[-1]
        ma_30 = crypto_data['close'].rolling(window=30).mean().iloc[-1]
        volatility = crypto_data['close'].pct_change().std() * 100
        
        # Determine trend
        if current_price > ma_7 > ma_30:
            trend = "strong uptrend"
        elif current_price > ma_7:
            trend = "uptrend"
        elif current_price < ma_7 < ma_30:
            trend = "strong downtrend"
        else:
            trend = "downtrend"
        
        message_text = f"""📈 {symbol} Technical Analysis

💰 Current Price: ${current_price:,.2f}
📊 7-Day MA: ${ma_7:,.2f}
📊 30-Day MA: ${ma_30:,.2f}
📉 Volatility: {volatility:.2f}%
🎯 Trend: {trend.upper()}

Market Analysis:
{symbol} is currently in a {trend}. The price is {'above' if current_price > ma_7 else 'below'} the 7-day moving average, 
indicating {'bullish' if current_price > ma_7 else 'bearish'} momentum in the short term.

Volatility: {'High' if volatility > 5 else 'Moderate' if volatility > 2 else 'Low'} - {volatility:.2f}%

Analysis based on 30-day historical data.
"""
        
        return {
            'success': True,
            'message': message_text,
            'intent': 'analysis',
            'symbol': symbol,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _handle_price_inquiry(self, symbol: str, message: str) -> Dict:
        """Handle price inquiry requests"""
        crypto_data = await self.fetch_crypto_data(symbol, days=1)
        
        if crypto_data is None:
            return {
                'success': False,
                'message': f"Sorry, I couldn't fetch the current price for {symbol}.",
                'timestamp': datetime.now().isoformat()
            }
        
        current_price = crypto_data['close'].iloc[-1]
        
        message_text = f"💰 The current price of {symbol} is ${current_price:,.2f}"
        
        return {
            'success': True,
            'message': message_text,
            'intent': 'price_inquiry',
            'symbol': symbol,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _handle_general_info(self, symbol: str, message: str) -> Dict:
        """Handle general information requests"""
        
        # If Groq AI is available, use it for detailed explanations
        if self.groq_available and self.groq_client:
            try:
                enhanced_message = f"Tell me about {symbol} cryptocurrency. Include its purpose, technology, use cases, and current market position."
                return await self._groq_ai_response(enhanced_message)
            except Exception as e:
                print(f"⚠️ Groq AI failed, using fallback info: {e}")
        
        # Fallback: Basic hardcoded info
        crypto_info = {
            'BTC': "Bitcoin is the first and largest cryptocurrency by market cap, created in 2009 by Satoshi Nakamoto.",
            'ETH': "Ethereum is a decentralized platform that enables smart contracts and decentralized applications (dApps).",
            'XRP': "XRP is a digital payment protocol and cryptocurrency designed for fast, low-cost international transfers.",
            'ADA': "Cardano is a proof-of-stake blockchain platform focused on sustainability and scalability.",
            'SOL': "Solana is a high-performance blockchain known for fast transactions and low fees.",
            'DOGE': "Dogecoin started as a meme cryptocurrency but has gained significant community support.",
            'BNB': "Binance Coin is the native token of the Binance exchange ecosystem.",
        }
        
        info = crypto_info.get(symbol, f"{symbol} is a cryptocurrency.")
        
        return {
            'success': True,
            'message': f"ℹ️ About {symbol}:\n\n{info}",
            'intent': 'general_info',
            'symbol': symbol,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _handle_general_query(self, message: str) -> Dict:
        """Handle general queries using Groq AI if available"""
        
        # If Groq AI is available, use it for comprehensive answers
        if self.groq_available and self.groq_client:
            try:
                return await self._groq_ai_response(message)
            except Exception as e:
                print(f"⚠️ Groq AI failed, using fallback: {e}")
        
        # Fallback response
        return {
            'success': True,
            'message': """👋 Hello! I'm your AI Crypto Analytics Assistant powered by machine learning models.

I can help you with:
- 📊 Price Predictions - Ask me to predict the future price of cryptocurrencies
- 📈 Technical Analysis - Get detailed technical indicators and trends
- 💰 Current Prices - Check real-time cryptocurrency prices
- ℹ️ Crypto Information - Learn about different cryptocurrencies

Supported cryptocurrencies: BTC, ETH, XRP, ADA, SOL, DOGE, BNB, DOT, MATIC, LTC, and more!

Try asking: "Predict Bitcoin price" or "Analyze Ethereum" or "What's the current price of BTC?"
""",
            'intent': 'general',
            'timestamp': datetime.now().isoformat()
        }
    
    async def _groq_ai_response(self, message: str) -> Dict:
        """
        Use Groq AI to answer comprehensive crypto questions
        This enables answering ALL crypto-related questions!
        """
        try:
            # Build context with recent chat history
            messages = [
                {
                    "role": "system",
                    "content": """You are a knowledgeable cryptocurrency and blockchain expert assistant. 
You have deep knowledge about:
- Cryptocurrencies (Bitcoin, Ethereum, and all major/minor coins)
- Blockchain technology and consensus mechanisms
- DeFi (Decentralized Finance) protocols and concepts
- NFTs and Web3 technologies
- Trading strategies and market analysis
- Technical and fundamental analysis
- Crypto regulations and compliance
- Mining and staking
- Wallets and security best practices
- Latest crypto news and developments

Provide accurate, helpful, and educational responses. Use emojis to make responses engaging.
Do NOT use bold markdown formatting (**text**) in your responses. Use plain text only.
If you don't know something, be honest about it. Always include relevant context and examples.
Never provide financial advice - only educational information."""
                }
            ]
            
            # Add recent chat history for context (last 5 messages)
            for msg in self.chat_history[-10:]:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Call Groq AI
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Current fast and knowledgeable model
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                top_p=0.9
            )
            
            ai_response = response.choices[0].message.content
            
            # Remove bold formatting from AI response
            ai_response = self.remove_bold_formatting(ai_response)
            
            return {
                'success': True,
                'message': ai_response,
                'intent': 'ai_response',
                'source': 'groq_ai',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Groq AI error: {e}")
            raise
    
    def get_chat_history(self, limit: int = 10) -> List[Dict]:
        """Get recent chat history"""
        return self.chat_history[-limit:]
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []


# Global chatbot instance
chatbot = None

def get_chatbot(groq_api_key: Optional[str] = None) -> CryptoAIChatbot:
    """Get or create chatbot instance"""
    global chatbot
    if chatbot is None:
        chatbot = CryptoAIChatbot(groq_api_key=groq_api_key)
    return chatbot
