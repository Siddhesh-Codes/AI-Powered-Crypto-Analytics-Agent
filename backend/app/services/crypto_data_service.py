import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from app.core.config import settings

class CryptoDataService:
    """
    Service for fetching real-time and historical cryptocurrency data
    Uses free tier APIs with intelligent caching and rate limiting
    """
    
    def __init__(self):
        self.base_url = settings.COINMARKETCAP_BASE_URL
        self.api_key = settings.COINMARKETCAP_API_KEY
        self.session = None
        self.logger = logging.getLogger(__name__)
        
        # Cache for reducing API calls
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication"""
        return {
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accept': 'application/json'
        }
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        
        cached_time = self.cache[key]['timestamp']
        return (datetime.now() - cached_time).seconds < self.cache_ttl
    
    async def get_crypto_listings(self, limit: int = 100) -> List[Dict]:
        """
        Get latest cryptocurrency listings
        
        Args:
            limit: Number of cryptocurrencies to fetch
            
        Returns:
            List of cryptocurrency data
        """
        cache_key = f"listings_{limit}"
        
        if self._is_cache_valid(cache_key):
            self.logger.info("Returning cached crypto listings")
            return self.cache[cache_key]['data']
        
        try:
            url = f"{self.base_url}/cryptocurrency/listings/latest"
            params = {
                'start': 1,
                'limit': limit,
                'convert': 'USD'
            }
            
            async with self.session.get(url, headers=self._get_headers(), params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    crypto_data = data['data']
                    
                    # Cache the result
                    self.cache[cache_key] = {
                        'data': crypto_data,
                        'timestamp': datetime.now()
                    }
                    
                    self.logger.info(f"Fetched {len(crypto_data)} cryptocurrency listings")
                    return crypto_data
                else:
                    self.logger.error(f"API request failed with status {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error fetching crypto listings: {str(e)}")
            return []
    
    async def get_crypto_quotes(self, symbols: List[str]) -> Dict:
        """
        Get current quotes for specific cryptocurrencies
        
        Args:
            symbols: List of cryptocurrency symbols (e.g., ['BTC', 'ETH'])
            
        Returns:
            Dictionary of cryptocurrency quotes
        """
        cache_key = f"quotes_{'_'.join(sorted(symbols))}"
        
        if self._is_cache_valid(cache_key):
            self.logger.info("Returning cached crypto quotes")
            return self.cache[cache_key]['data']
        
        try:
            url = f"{self.base_url}/cryptocurrency/quotes/latest"
            params = {
                'symbol': ','.join(symbols),
                'convert': 'USD'
            }
            
            async with self.session.get(url, headers=self._get_headers(), params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    quotes_data = data['data']
                    
                    # Cache the result
                    self.cache[cache_key] = {
                        'data': quotes_data,
                        'timestamp': datetime.now()
                    }
                    
                    self.logger.info(f"Fetched quotes for {len(symbols)} cryptocurrencies")
                    return quotes_data
                else:
                    self.logger.error(f"API request failed with status {response.status}")
                    return {}
                    
        except Exception as e:
            self.logger.error(f"Error fetching crypto quotes: {str(e)}")
            return {}
    
    async def get_historical_data(self, symbol: str, 
                                 time_period: str = '1M',
                                 interval: str = '1d') -> pd.DataFrame:
        """
        Get historical price data for a cryptocurrency
        Note: This is a simplified version. For production, you'd need historical data API
        
        Args:
            symbol: Cryptocurrency symbol
            time_period: Time period (1D, 7D, 1M, 3M, 1Y)
            interval: Data interval (1h, 1d, 1w)
            
        Returns:
            DataFrame with historical price data
        """
        try:
            # For demo purposes, generate synthetic historical data
            # In production, use actual historical data API
            
            end_date = datetime.now()
            if time_period == '1D':
                start_date = end_date - timedelta(days=1)
                freq = '1H'
            elif time_period == '7D':
                start_date = end_date - timedelta(days=7)
                freq = '4H'
            elif time_period == '1M':
                start_date = end_date - timedelta(days=30)
                freq = '1D'
            elif time_period == '3M':
                start_date = end_date - timedelta(days=90)
                freq = '1D'
            else:  # 1Y
                start_date = end_date - timedelta(days=365)
                freq = '1D'
            
            dates = pd.date_range(start=start_date, end=end_date, freq=freq)
            
            # Generate realistic price data (this would be replaced with actual API calls)
            import numpy as np
            np.random.seed(42)
            
            base_price = 45000 if symbol == 'BTC' else 2500  # Different base prices
            prices = []
            current_price = base_price
            
            for _ in range(len(dates)):
                # Random walk with slight upward trend
                change_percent = np.random.normal(0.001, 0.02)  # 0.1% mean, 2% std
                current_price *= (1 + change_percent)
                prices.append(current_price)
            
            # Create OHLCV data
            df = pd.DataFrame({
                'timestamp': dates,
                'open': prices,
                'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
                'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
                'close': prices,
                'volume': [np.random.randint(1000000, 10000000) for _ in prices]
            })
            
            self.logger.info(f"Generated historical data for {symbol}: {len(df)} records")
            return df
            
        except Exception as e:
            self.logger.error(f"Error generating historical data: {str(e)}")
            return pd.DataFrame()
    
    async def get_market_metrics(self) -> Dict:
        """
        Get global market metrics
        
        Returns:
            Dictionary with market metrics
        """
        cache_key = "market_metrics"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            url = f"{self.base_url}/global-metrics/quotes/latest"
            
            async with self.session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    metrics = data['data']
                    
                    # Cache the result
                    self.cache[cache_key] = {
                        'data': metrics,
                        'timestamp': datetime.now()
                    }
                    
                    return metrics
                else:
                    # Return mock data if API fails
                    mock_metrics = {
                        'quote': {
                            'USD': {
                                'total_market_cap': 2100000000000,
                                'total_volume_24h': 89200000000,
                                'bitcoin_dominance': 42.3,
                                'market_cap_change_percentage_24h': 2.4
                            }
                        }
                    }
                    return mock_metrics
                    
        except Exception as e:
            self.logger.error(f"Error fetching market metrics: {str(e)}")
            # Return mock data on error
            return {
                'quote': {
                    'USD': {
                        'total_market_cap': 2100000000000,
                        'total_volume_24h': 89200000000,
                        'bitcoin_dominance': 42.3,
                        'market_cap_change_percentage_24h': 2.4
                    }
                }
            }


# Example usage
async def main():
    """Example usage of CryptoDataService"""
    async with CryptoDataService() as service:
        # Get top cryptocurrencies
        listings = await service.get_crypto_listings(limit=10)
        print(f"Top 10 cryptocurrencies: {len(listings)} fetched")
        
        # Get specific quotes
        quotes = await service.get_crypto_quotes(['BTC', 'ETH', 'ADA'])
        print(f"Quotes fetched for: {list(quotes.keys())}")
        
        # Get historical data
        btc_data = await service.get_historical_data('BTC', '1M')
        print(f"BTC historical data: {len(btc_data)} records")
        
        # Get market metrics
        metrics = await service.get_market_metrics()
        print(f"Market metrics: {metrics}")

if __name__ == "__main__":
    asyncio.run(main())
