"""
WebSocket Manager for Real-time Cryptocurrency Data
Provides real-time price updates, alerts, and market data
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Set, Optional
import asyncio
import json
import aiohttp
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

class SubscriptionType(Enum):
    PRICE_UPDATES = "price_updates"
    PORTFOLIO_UPDATES = "portfolio_updates"
    NEWS_UPDATES = "news_updates"
    ALERTS = "alerts"
    TECHNICAL_INDICATORS = "technical_indicators"

@dataclass
class ClientSubscription:
    client_id: str
    websocket: WebSocket
    subscriptions: Set[SubscriptionType]
    watched_coins: Set[str]
    user_id: Optional[str] = None

class WebSocketManager:
    """
    Manages WebSocket connections and real-time data distribution
    """
    
    def __init__(self):
        self.active_connections: List[ClientSubscription] = []
        self.price_cache: Dict[str, Dict[str, Any]] = {}
        self.last_update: Dict[str, datetime] = {}
        self.update_tasks: Dict[str, asyncio.Task] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str) -> ClientSubscription:
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        client = ClientSubscription(
            client_id=client_id,
            websocket=websocket,
            subscriptions=set(),
            watched_coins=set()
        )
        
        self.active_connections.append(client)
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat(),
            "available_subscriptions": [sub.value for sub in SubscriptionType]
        }, websocket)
        
        return client
    
    def disconnect(self, client: ClientSubscription):
        """Remove a WebSocket connection"""
        if client in self.active_connections:
            self.active_connections.remove(client)
        
        # Clean up tasks if no more clients need them
        self._cleanup_unused_tasks()
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logging.error(f"Error sending message: {e}")
    
    async def broadcast_to_subscribers(self, message: Dict[str, Any], subscription_type: SubscriptionType, coin: str = None):
        """Broadcast message to all subscribers of a specific type"""
        disconnected_clients = []
        
        for client in self.active_connections:
            try:
                # Check if client is subscribed to this type
                if subscription_type not in client.subscriptions:
                    continue
                
                # Check if client is watching this coin (if applicable)
                if coin and coin not in client.watched_coins:
                    continue
                
                await self.send_personal_message(message, client.websocket)
                
            except WebSocketDisconnect:
                disconnected_clients.append(client)
            except Exception as e:
                logging.error(f"Error broadcasting to client {client.client_id}: {e}")
                disconnected_clients.append(client)
        
        # Clean up disconnected clients
        for client in disconnected_clients:
            self.disconnect(client)
    
    async def subscribe_client(self, client: ClientSubscription, subscription_type: SubscriptionType, coins: List[str] = None):
        """Subscribe a client to a specific data type"""
        client.subscriptions.add(subscription_type)
        
        if coins:
            client.watched_coins.update(coins)
        
        # Start relevant update tasks
        await self._start_update_tasks(subscription_type, coins or [])
        
        # Send confirmation
        await self.send_personal_message({
            "type": "subscription_confirmed",
            "subscription_type": subscription_type.value,
            "watched_coins": list(client.watched_coins) if coins else None,
            "timestamp": datetime.now().isoformat()
        }, client.websocket)
    
    async def unsubscribe_client(self, client: ClientSubscription, subscription_type: SubscriptionType):
        """Unsubscribe a client from a specific data type"""
        client.subscriptions.discard(subscription_type)
        
        await self.send_personal_message({
            "type": "unsubscription_confirmed",
            "subscription_type": subscription_type.value,
            "timestamp": datetime.now().isoformat()
        }, client.websocket)
        
        # Clean up tasks if no more clients need them
        self._cleanup_unused_tasks()
    
    async def _start_update_tasks(self, subscription_type: SubscriptionType, coins: List[str]):
        """Start background tasks for data updates"""
        
        if subscription_type == SubscriptionType.PRICE_UPDATES:
            for coin in coins:
                task_key = f"price_{coin}"
                if task_key not in self.update_tasks:
                    self.update_tasks[task_key] = asyncio.create_task(
                        self._price_update_loop(coin)
                    )
        
        elif subscription_type == SubscriptionType.NEWS_UPDATES:
            task_key = "news_updates"
            if task_key not in self.update_tasks:
                self.update_tasks[task_key] = asyncio.create_task(
                    self._news_update_loop()
                )
        
        elif subscription_type == SubscriptionType.TECHNICAL_INDICATORS:
            for coin in coins:
                task_key = f"indicators_{coin}"
                if task_key not in self.update_tasks:
                    self.update_tasks[task_key] = asyncio.create_task(
                        self._indicators_update_loop(coin)
                    )
    
    async def _price_update_loop(self, coin: str):
        """Background task for price updates"""
        while True:
            try:
                # Check if any clients are still subscribed
                has_subscribers = any(
                    SubscriptionType.PRICE_UPDATES in client.subscriptions and 
                    coin in client.watched_coins
                    for client in self.active_connections
                )
                
                if not has_subscribers:
                    break
                
                # Fetch price data
                price_data = await self._fetch_price_data(coin)
                
                if price_data:
                    # Update cache
                    self.price_cache[coin] = price_data
                    self.last_update[coin] = datetime.now()
                    
                    # Broadcast to subscribers
                    await self.broadcast_to_subscribers(
                        {
                            "type": "price_update",
                            "coin": coin,
                            "data": price_data,
                            "timestamp": datetime.now().isoformat()
                        },
                        SubscriptionType.PRICE_UPDATES,
                        coin
                    )
                
                # Wait before next update (30 seconds for price data)
                await asyncio.sleep(30)
                
            except Exception as e:
                logging.error(f"Error in price update loop for {coin}: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _news_update_loop(self):
        """Background task for news updates"""
        last_check = datetime.now()
        
        while True:
            try:
                # Check if any clients are subscribed
                has_subscribers = any(
                    SubscriptionType.NEWS_UPDATES in client.subscriptions
                    for client in self.active_connections
                )
                
                if not has_subscribers:
                    break
                
                # Fetch latest news (only new articles since last check)
                from news_sentiment import news_client
                articles = await news_client.get_crypto_news(limit=10, hours_back=2)
                
                # Filter for articles newer than last check
                new_articles = [
                    article for article in articles
                    if datetime.fromisoformat(article.get('published_at', '').replace('Z', '+00:00')) > last_check
                ]
                
                if new_articles:
                    await self.broadcast_to_subscribers(
                        {
                            "type": "news_update",
                            "new_articles": new_articles,
                            "count": len(new_articles),
                            "timestamp": datetime.now().isoformat()
                        },
                        SubscriptionType.NEWS_UPDATES
                    )
                
                last_check = datetime.now()
                
                # Wait 5 minutes between news checks
                await asyncio.sleep(300)
                
            except Exception as e:
                logging.error(f"Error in news update loop: {e}")
                await asyncio.sleep(600)  # Wait longer on error
    
    async def _indicators_update_loop(self, coin: str):
        """Background task for technical indicators updates"""
        while True:
            try:
                # Check if any clients are still subscribed
                has_subscribers = any(
                    SubscriptionType.TECHNICAL_INDICATORS in client.subscriptions and 
                    coin in client.watched_coins
                    for client in self.active_connections
                )
                
                if not has_subscribers:
                    break
                
                # Fetch and calculate technical indicators
                from technical_indicators import CryptoDataFetcher, analyze_technical_indicators
                
                data_fetcher = CryptoDataFetcher()
                price_data = await data_fetcher.get_price_history(coin, 30)
                
                if price_data.get('success'):
                    analysis = analyze_technical_indicators(price_data['data'])
                    
                    await self.broadcast_to_subscribers(
                        {
                            "type": "technical_indicators_update",
                            "coin": coin,
                            "indicators": {
                                "rsi": analysis.get('rsi', [])[-1:],
                                "signals": analysis.get('signals', {}),
                                "trend": analysis.get('signals', {}).get('overall_sentiment', 'neutral')
                            },
                            "timestamp": datetime.now().isoformat()
                        },
                        SubscriptionType.TECHNICAL_INDICATORS,
                        coin
                    )
                
                # Update every 2 minutes for technical indicators
                await asyncio.sleep(120)
                
            except Exception as e:
                logging.error(f"Error in indicators update loop for {coin}: {e}")
                await asyncio.sleep(300)  # Wait longer on error
    
    async def _fetch_price_data(self, coin: str) -> Dict[str, Any]:
        """Fetch current price data for a coin"""
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if coin in data:
                            coin_data = data[coin]
                            return {
                                'price': coin_data.get('usd', 0),
                                'price_change_24h': coin_data.get('usd_24h_change', 0),
                                'volume_24h': coin_data.get('usd_24h_vol', 0),
                                'market_cap': coin_data.get('usd_market_cap', 0)
                            }
            
            return None
            
        except Exception as e:
            logging.error(f"Error fetching price data for {coin}: {e}")
            return None
    
    def _cleanup_unused_tasks(self):
        """Clean up background tasks that are no longer needed"""
        tasks_to_remove = []
        
        for task_key, task in self.update_tasks.items():
            if task_key.startswith('price_'):
                coin = task_key.replace('price_', '')
                has_subscribers = any(
                    SubscriptionType.PRICE_UPDATES in client.subscriptions and 
                    coin in client.watched_coins
                    for client in self.active_connections
                )
                if not has_subscribers:
                    task.cancel()
                    tasks_to_remove.append(task_key)
            
            elif task_key.startswith('indicators_'):
                coin = task_key.replace('indicators_', '')
                has_subscribers = any(
                    SubscriptionType.TECHNICAL_INDICATORS in client.subscriptions and 
                    coin in client.watched_coins
                    for client in self.active_connections
                )
                if not has_subscribers:
                    task.cancel()
                    tasks_to_remove.append(task_key)
            
            elif task_key == 'news_updates':
                has_subscribers = any(
                    SubscriptionType.NEWS_UPDATES in client.subscriptions
                    for client in self.active_connections
                )
                if not has_subscribers:
                    task.cancel()
                    tasks_to_remove.append(task_key)
        
        for task_key in tasks_to_remove:
            del self.update_tasks[task_key]
    
    async def send_alert(self, user_id: str, alert_data: Dict[str, Any]):
        """Send an alert to a specific user"""
        user_clients = [
            client for client in self.active_connections 
            if client.user_id == user_id and SubscriptionType.ALERTS in client.subscriptions
        ]
        
        for client in user_clients:
            await self.send_personal_message({
                "type": "alert",
                "data": alert_data,
                "timestamp": datetime.now().isoformat()
            }, client.websocket)

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
