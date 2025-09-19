"""
Technical Indicators Module
Implements RSI, MACD, Bollinger Bands, Moving Averages, and other technical indicators
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
import asyncio
import aiohttp

class TechnicalIndicators:
    """
    Technical analysis indicators for cryptocurrency price data
    """
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """Calculate Relative Strength Index (RSI)"""
        if len(prices) < period + 1:
            return []
        
        df = pd.DataFrame({'close': prices})
        delta = df['close'].diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.dropna().tolist()
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, List[float]]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow + signal:
            return {"macd": [], "signal": [], "histogram": []}
        
        df = pd.DataFrame({'close': prices})
        
        # Calculate MACD
        ema_fast = df['close'].ewm(span=fast).mean()
        ema_slow = df['close'].ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        
        # Calculate signal line
        signal_line = macd.ewm(span=signal).mean()
        
        # Calculate histogram
        histogram = macd - signal_line
        
        return {
            "macd": macd.dropna().tolist(),
            "signal": signal_line.dropna().tolist(),
            "histogram": histogram.dropna().tolist()
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2) -> Dict[str, List[float]]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {"upper": [], "middle": [], "lower": []}
        
        df = pd.DataFrame({'close': prices})
        
        # Calculate moving average (middle band)
        middle = df['close'].rolling(window=period).mean()
        
        # Calculate standard deviation
        std = df['close'].rolling(window=period).std()
        
        # Calculate upper and lower bands
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            "upper": upper.dropna().tolist(),
            "middle": middle.dropna().tolist(),
            "lower": lower.dropna().tolist()
        }
    
    @staticmethod
    def calculate_moving_averages(prices: List[float], periods: List[int] = [20, 50, 200]) -> Dict[str, List[float]]:
        """Calculate Simple Moving Averages for multiple periods"""
        if not prices:
            return {}
        
        df = pd.DataFrame({'close': prices})
        result = {}
        
        for period in periods:
            if len(prices) >= period:
                ma = df['close'].rolling(window=period).mean()
                result[f"sma_{period}"] = ma.dropna().tolist()
            else:
                result[f"sma_{period}"] = []
        
        return result
    
    @staticmethod
    def calculate_stochastic(highs: List[float], lows: List[float], closes: List[float], 
                           k_period: int = 14, d_period: int = 3) -> Dict[str, List[float]]:
        """Calculate Stochastic Oscillator"""
        if len(closes) < k_period:
            return {"k": [], "d": []}
        
        df = pd.DataFrame({'high': highs, 'low': lows, 'close': closes})
        
        # Calculate %K
        lowest_low = df['low'].rolling(window=k_period).min()
        highest_high = df['high'].rolling(window=k_period).max()
        k_percent = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
        
        # Calculate %D (moving average of %K)
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            "k": k_percent.dropna().tolist(),
            "d": d_percent.dropna().tolist()
        }
    
    @staticmethod 
    def calculate_williams_r(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
        """Calculate Williams %R"""
        if len(closes) < period:
            return []
        
        df = pd.DataFrame({'high': highs, 'low': lows, 'close': closes})
        
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()
        
        williams_r = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
        
        return williams_r.dropna().tolist()
    
    @staticmethod
    def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
        """Calculate Average True Range (ATR)"""
        if len(closes) < period + 1:
            return []
        
        df = pd.DataFrame({'high': highs, 'low': lows, 'close': closes})
        
        # Calculate True Range
        high_low = df['high'] - df['low']
        high_close_prev = abs(df['high'] - df['close'].shift(1))
        low_close_prev = abs(df['low'] - df['close'].shift(1))
        
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        
        # Calculate ATR
        atr = true_range.rolling(window=period).mean()
        
        return atr.dropna().tolist()

class CryptoDataFetcher:
    """
    Fetch cryptocurrency price data from various APIs
    """
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = None
    
    async def get_price_history(self, coin_id: str, days: int = 30) -> Dict[str, Any]:
        """Fetch historical price data"""
        try:
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily' if days > 1 else 'hourly'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract OHLC data
                        prices = [price[1] for price in data.get('prices', [])]
                        timestamps = [price[0] for price in data.get('prices', [])]
                        
                        # For proper OHLC, we'll approximate from price data
                        ohlc_data = []
                        for i, price in enumerate(prices):
                            # Simple approximation - in production, use proper OHLC data
                            high = price * 1.02  # Approximate 2% high
                            low = price * 0.98   # Approximate 2% low
                            
                            ohlc_data.append({
                                'timestamp': timestamps[i],
                                'open': price,
                                'high': high,
                                'low': low,
                                'close': price,
                                'volume': 0  # Would need separate volume data
                            })
                        
                        return {
                            'success': True,
                            'data': ohlc_data,
                            'prices': prices
                        }
                    else:
                        return {'success': False, 'error': f'API returned {response.status}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def get_multiple_coins_data(self, coin_ids: List[str], days: int = 30) -> Dict[str, Any]:
        """Fetch data for multiple coins concurrently"""
        tasks = []
        for coin_id in coin_ids:
            tasks.append(self.get_price_history(coin_id, days))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        coin_data = {}
        for i, result in enumerate(results):
            if isinstance(result, dict) and result.get('success'):
                coin_data[coin_ids[i]] = result['data']
            else:
                coin_data[coin_ids[i]] = None
        
        return coin_data

def analyze_technical_indicators(ohlc_data: List[Dict]) -> Dict[str, Any]:
    """
    Analyze technical indicators for given OHLC data
    """
    if not ohlc_data:
        return {"error": "No data provided"}
    
    # Extract price arrays
    closes = [item['close'] for item in ohlc_data]
    highs = [item['high'] for item in ohlc_data]
    lows = [item['low'] for item in ohlc_data]
    
    indicators = TechnicalIndicators()
    
    analysis = {
        'rsi': indicators.calculate_rsi(closes),
        'macd': indicators.calculate_macd(closes),
        'bollinger_bands': indicators.calculate_bollinger_bands(closes),
        'moving_averages': indicators.calculate_moving_averages(closes),
        'stochastic': indicators.calculate_stochastic(highs, lows, closes),
        'williams_r': indicators.calculate_williams_r(highs, lows, closes),
        'atr': indicators.calculate_atr(highs, lows, closes)
    }
    
    # Generate trading signals based on indicators
    signals = generate_trading_signals(analysis, closes)
    analysis['signals'] = signals
    
    return analysis

def generate_trading_signals(indicators: Dict[str, Any], prices: List[float]) -> Dict[str, Any]:
    """
    Generate trading signals based on technical indicators
    """
    signals = {
        'overall_sentiment': 'neutral',
        'strength': 0,
        'recommendations': []
    }
    
    try:
        # RSI signals
        if indicators.get('rsi'):
            latest_rsi = indicators['rsi'][-1]
            if latest_rsi > 70:
                signals['recommendations'].append({
                    'type': 'sell',
                    'reason': f'RSI overbought at {latest_rsi:.2f}',
                    'strength': 'medium'
                })
            elif latest_rsi < 30:
                signals['recommendations'].append({
                    'type': 'buy',
                    'reason': f'RSI oversold at {latest_rsi:.2f}',
                    'strength': 'medium'
                })
        
        # MACD signals
        if indicators.get('macd'):
            macd_data = indicators['macd']
            if len(macd_data['macd']) >= 2:
                current_macd = macd_data['macd'][-1]
                current_signal = macd_data['signal'][-1]
                
                if current_macd > current_signal:
                    signals['recommendations'].append({
                        'type': 'buy',
                        'reason': 'MACD above signal line',
                        'strength': 'medium'
                    })
                else:
                    signals['recommendations'].append({
                        'type': 'sell',
                        'reason': 'MACD below signal line',
                        'strength': 'medium'
                    })
        
        # Moving average signals
        if indicators.get('moving_averages'):
            ma_data = indicators['moving_averages']
            current_price = prices[-1]
            
            if 'sma_20' in ma_data and ma_data['sma_20']:
                sma_20 = ma_data['sma_20'][-1]
                if current_price > sma_20:
                    signals['recommendations'].append({
                        'type': 'buy',
                        'reason': 'Price above 20-day MA',
                        'strength': 'low'
                    })
        
        # Calculate overall sentiment
        buy_signals = len([s for s in signals['recommendations'] if s['type'] == 'buy'])
        sell_signals = len([s for s in signals['recommendations'] if s['type'] == 'sell'])
        
        if buy_signals > sell_signals:
            signals['overall_sentiment'] = 'bullish'
            signals['strength'] = min(buy_signals / (buy_signals + sell_signals) * 100, 100)
        elif sell_signals > buy_signals:
            signals['overall_sentiment'] = 'bearish'
            signals['strength'] = min(sell_signals / (buy_signals + sell_signals) * 100, 100)
        
    except Exception as e:
        signals['error'] = str(e)
    
    return signals
