"""
News and Sentiment Analysis Module
Integrates with news APIs and provides sentiment analysis for cryptocurrency news
"""

import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
import os
from textblob import TextBlob
import requests

class NewsAPIClient:
    """
    News API client for fetching cryptocurrency news
    """
    
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY", "")  # Get from newsapi.org
        self.base_url = "https://newsapi.org/v2"
        self.crypto_keywords = [
            "bitcoin", "ethereum", "cryptocurrency", "crypto", "blockchain",
            "btc", "eth", "altcoin", "defi", "nft", "web3", "dogecoin", "cardano"
        ]
    
    async def get_crypto_news(self, limit: int = 20, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Fetch latest cryptocurrency news"""
        try:
            if not self.news_api_key:
                return await self._get_mock_news(limit)
            
            # Calculate date range
            from_date = (datetime.now() - timedelta(hours=hours_back)).isoformat()
            
            # Search for crypto-related news
            query = " OR ".join(self.crypto_keywords[:5])  # Limit query length
            
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': min(limit, 100),
                'apiKey': self.news_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/everything"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get('articles', [])
                        
                        # Process and analyze articles
                        processed_articles = []
                        for article in articles[:limit]:
                            processed_article = await self._process_article(article)
                            processed_articles.append(processed_article)
                        
                        return processed_articles
                    else:
                        print(f"News API error: {response.status}")
                        return await self._get_mock_news(limit)
        
        except Exception as e:
            print(f"Error fetching news: {e}")
            return await self._get_mock_news(limit)
    
    async def _process_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Process and analyze a news article"""
        title = article.get('title', '')
        description = article.get('description', '')
        content = article.get('content', '')
        
        # Combine text for sentiment analysis
        full_text = f"{title} {description} {content}"
        
        # Perform sentiment analysis
        sentiment_data = self._analyze_sentiment(full_text)
        
        # Extract mentioned cryptocurrencies
        mentioned_cryptos = self._extract_crypto_mentions(full_text)
        
        return {
            'id': hash(article.get('url', title)) % 1000000,
            'title': title,
            'description': description[:300] if description else '',
            'url': article.get('url', ''),
            'published_at': article.get('publishedAt', ''),
            'source': article.get('source', {}).get('name', 'Unknown'),
            'image_url': article.get('urlToImage', ''),
            'sentiment': sentiment_data,
            'mentioned_cryptos': mentioned_cryptos,
            'relevance_score': self._calculate_relevance_score(full_text)
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Convert polarity to sentiment label
            if polarity > 0.1:
                sentiment_label = "positive"
            elif polarity < -0.1:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
            
            return {
                'label': sentiment_label,
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3),
                'confidence': abs(polarity)
            }
        
        except Exception as e:
            return {
                'label': 'neutral',
                'polarity': 0,
                'subjectivity': 0.5,
                'confidence': 0,
                'error': str(e)
            }
    
    def _extract_crypto_mentions(self, text: str) -> List[str]:
        """Extract cryptocurrency mentions from text"""
        text_lower = text.lower()
        mentions = []
        
        crypto_patterns = {
            'bitcoin': ['bitcoin', 'btc'],
            'ethereum': ['ethereum', 'eth', 'ether'],
            'cardano': ['cardano', 'ada'],
            'solana': ['solana', 'sol'],
            'dogecoin': ['dogecoin', 'doge'],
            'ripple': ['ripple', 'xrp'],
            'polkadot': ['polkadot', 'dot'],
            'chainlink': ['chainlink', 'link'],
            'litecoin': ['litecoin', 'ltc'],
            'avalanche': ['avalanche', 'avax']
        }
        
        for crypto, patterns in crypto_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    mentions.append(crypto)
                    break
        
        return list(set(mentions))  # Remove duplicates
    
    def _calculate_relevance_score(self, text: str) -> float:
        """Calculate how relevant the article is to cryptocurrency"""
        text_lower = text.lower()
        score = 0
        
        # Base crypto keywords
        crypto_keywords = ['crypto', 'bitcoin', 'ethereum', 'blockchain', 'defi']
        for keyword in crypto_keywords:
            score += text_lower.count(keyword) * 2
        
        # Technical terms
        tech_terms = ['mining', 'wallet', 'exchange', 'trading', 'price', 'market']
        for term in tech_terms:
            score += text_lower.count(term)
        
        # Normalize score (0-1)
        max_score = len(text.split()) * 0.1  # Assume max 10% keyword density
        return min(score / max_score if max_score > 0 else 0, 1.0)
    
    async def _get_mock_news(self, limit: int) -> List[Dict[str, Any]]:
        """Generate mock news data when API is not available"""
        mock_articles = [
            {
                'id': 1,
                'title': 'Bitcoin Surges to New All-Time High Amid Institutional Adoption',
                'description': 'Major financial institutions continue to adopt Bitcoin as a treasury asset, driving prices higher.',
                'url': 'https://example.com/bitcoin-ath',
                'published_at': datetime.now().isoformat(),
                'source': 'CryptoNews',
                'image_url': '',
                'sentiment': {'label': 'positive', 'polarity': 0.7, 'subjectivity': 0.6, 'confidence': 0.7},
                'mentioned_cryptos': ['bitcoin'],
                'relevance_score': 0.9
            },
            {
                'id': 2,
                'title': 'Ethereum 2.0 Staking Rewards Reach Record Levels',
                'description': 'The Ethereum network sees increased participation in staking with attractive rewards.',
                'url': 'https://example.com/eth-staking',
                'published_at': (datetime.now() - timedelta(hours=2)).isoformat(),
                'source': 'CoinDesk',
                'image_url': '',
                'sentiment': {'label': 'positive', 'polarity': 0.5, 'subjectivity': 0.4, 'confidence': 0.5},
                'mentioned_cryptos': ['ethereum'],
                'relevance_score': 0.8
            },
            {
                'id': 3,
                'title': 'Regulatory Concerns Impact Crypto Market Sentiment',
                'description': 'New regulatory proposals cause uncertainty in cryptocurrency markets.',
                'url': 'https://example.com/regulatory-news',
                'published_at': (datetime.now() - timedelta(hours=4)).isoformat(),
                'source': 'The Block',
                'image_url': '',
                'sentiment': {'label': 'negative', 'polarity': -0.4, 'subjectivity': 0.7, 'confidence': 0.4},
                'mentioned_cryptos': ['bitcoin', 'ethereum'],
                'relevance_score': 0.7
            }
        ]
        
        return mock_articles[:limit]

class SentimentAnalyzer:
    """
    Advanced sentiment analysis for cryptocurrency content
    """
    
    def __init__(self):
        self.crypto_positive_words = [
            'surge', 'bullish', 'rally', 'gain', 'up', 'rise', 'boom', 'adoption',
            'breakthrough', 'partnership', 'investment', 'upgrade', 'launch'
        ]
        self.crypto_negative_words = [
            'crash', 'bearish', 'dump', 'fall', 'down', 'decline', 'ban', 'regulation',
            'hack', 'scam', 'bubble', 'volatility', 'uncertainty'
        ]
    
    def analyze_market_sentiment(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall market sentiment from news articles"""
        if not articles:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0,
                'confidence': 0,
                'article_count': 0
            }
        
        total_polarity = 0
        weighted_polarity = 0
        total_weight = 0
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for article in articles:
            sentiment = article.get('sentiment', {})
            polarity = sentiment.get('polarity', 0)
            relevance = article.get('relevance_score', 0.5)
            
            # Weight by relevance
            weight = relevance * sentiment.get('confidence', 0.5)
            weighted_polarity += polarity * weight
            total_weight += weight
            
            # Count sentiment labels
            label = sentiment.get('label', 'neutral')
            sentiment_counts[label] += 1
        
        # Calculate overall sentiment
        if total_weight > 0:
            overall_polarity = weighted_polarity / total_weight
        else:
            overall_polarity = 0
        
        # Determine overall sentiment label
        if overall_polarity > 0.1:
            overall_sentiment = 'positive'
        elif overall_polarity < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_score': round(overall_polarity, 3),
            'confidence': min(abs(overall_polarity) * 2, 1.0),
            'article_count': len(articles),
            'sentiment_distribution': sentiment_counts,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def get_coin_specific_sentiment(self, articles: List[Dict[str, Any]], coin: str) -> Dict[str, Any]:
        """Get sentiment analysis for a specific cryptocurrency"""
        relevant_articles = [
            article for article in articles 
            if coin.lower() in article.get('mentioned_cryptos', [])
        ]
        
        if not relevant_articles:
            return {
                'coin': coin,
                'sentiment': 'neutral',
                'score': 0,
                'article_count': 0,
                'confidence': 0
            }
        
        sentiment_analysis = self.analyze_market_sentiment(relevant_articles)
        sentiment_analysis['coin'] = coin
        
        return sentiment_analysis

# Initialize global instances
news_client = NewsAPIClient()
sentiment_analyzer = SentimentAnalyzer()
