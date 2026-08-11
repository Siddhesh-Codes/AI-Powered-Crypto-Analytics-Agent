import React, { useState, useEffect, useRef } from 'react';
import { API_CONFIG } from '../config/api';

interface PriceData {
  coin_id: string;
  current_price: number;
  price_change_24h: number;
  last_updated: string;
}

interface NewsItem {
  title: string;
  description: string;
  url: string;
  publishedAt: string;
  sentiment: {
    polarity: number;
    subjectivity: number;
    label: string;
  };
}

const RealTimeData = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [priceData, setPriceData] = useState<Record<string, PriceData>>({});
  const [news, setNews] = useState<NewsItem[]>([]);
  const [subscriptions, setSubscriptions] = useState<Set<string>>(new Set(['bitcoin', 'ethereum']));
  const ws = useRef<WebSocket | null>(null);
  const clientId = useRef(`client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = `${API_CONFIG.WS_URL}/ws/${clientId.current}`;
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connected');
        
        // Subscribe to initial coins
        Array.from(subscriptions).forEach(coinId => {
          ws.current?.send(JSON.stringify({
            type: 'subscribe',
            subscription_type: 'prices',
            coin_id: coinId
          }));
        });

        // Subscribe to news
        ws.current?.send(JSON.stringify({
          type: 'subscribe',
          subscription_type: 'news'
        }));
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'price_update':
              setPriceData(prev => ({
                ...prev,
                [data.data.coin_id]: data.data
              }));
              break;
              
            case 'news_update':
              setNews(prev => [...data.data, ...prev].slice(0, 10)); // Keep latest 10 news items
              break;
              
            case 'technical_indicator_update':
              // Handle technical indicator updates
              console.log('Technical indicator update:', data.data);
              break;
              
            default:
              console.log('Unknown message type:', data.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.current.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');
        
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    };

    connectWebSocket();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const subscribeToCoin = (coinId: string) => {
    if (!subscriptions.has(coinId) && ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'subscribe',
        subscription_type: 'prices',
        coin_id: coinId
      }));
      setSubscriptions(prev => new Set([...Array.from(prev), coinId]));
    }
  };

  const unsubscribeFromCoin = (coinId: string) => {
    if (subscriptions.has(coinId) && ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'unsubscribe',
        subscription_type: 'prices',
        coin_id: coinId
      }));
      setSubscriptions(prev => {
        const newSet = new Set(prev);
        newSet.delete(coinId);
        return newSet;
      });
      setPriceData(prev => {
        const newData = { ...prev };
        delete newData[coinId];
        return newData;
      });
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 6
    }).format(price);
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      timeZone: 'Asia/Kolkata',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }).replace(/am/i, 'AM').replace(/pm/i, 'PM');
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive': return 'text-green-600 bg-green-100';
      case 'negative': return 'text-red-600 bg-red-100';
      case 'neutral': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const popularCoins = ['bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana', 'dogecoin', 'polkadot'];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Real-Time Market Data</h2>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className={`text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>

        {/* Price Data Section */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Live Prices</h3>
          
          {/* Coin Subscription Controls */}
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">Add/Remove Coins:</p>
            <div className="flex flex-wrap gap-2">
              {popularCoins.map(coinId => (
                <button
                  key={coinId}
                  onClick={() => subscriptions.has(coinId) ? unsubscribeFromCoin(coinId) : subscribeToCoin(coinId)}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    subscriptions.has(coinId)
                      ? 'bg-blue-500 text-white hover:bg-blue-600'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {coinId} {subscriptions.has(coinId) ? '✓' : '+'}
                </button>
              ))}
            </div>
          </div>

          {/* Price Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(priceData).map(([coinId, data]) => (
              <div key={coinId} className="bg-gray-50 rounded-lg p-4 border">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-gray-800 capitalize">{coinId}</h4>
                  <button
                    onClick={() => unsubscribeFromCoin(coinId)}
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    ✕
                  </button>
                </div>
                <div className="text-2xl font-bold text-blue-600 mb-1">
                  {formatPrice(data.current_price)}
                </div>
                <div className={`text-sm font-medium ${
                  data.price_change_24h > 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {data.price_change_24h > 0 ? '+' : ''}{data.price_change_24h.toFixed(2)}%
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Updated: {formatTime(data.last_updated)}
                </div>
              </div>
            ))}
          </div>

          {Object.keys(priceData).length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <p>No price data available. Add some coins to get started!</p>
            </div>
          )}
        </div>

        {/* News Section */}
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Latest Crypto News</h3>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {news.map((item, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-4 border">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-semibold text-gray-800 text-sm line-clamp-2">
                    <a 
                      href={item.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="hover:text-blue-600 transition-colors"
                    >
                      {item.title}
                    </a>
                  </h4>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getSentimentColor(item.sentiment.label)}`}>
                    {item.sentiment.label}
                  </span>
                </div>
                <p className="text-gray-600 text-sm mb-2 line-clamp-2">
                  {item.description}
                </p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{new Date(item.publishedAt).toLocaleString()}</span>
                  <span>
                    Sentiment: {(item.sentiment.polarity * 100).toFixed(0)}% 
                    ({item.sentiment.polarity > 0 ? 'Positive' : item.sentiment.polarity < 0 ? 'Negative' : 'Neutral'})
                  </span>
                </div>
              </div>
            ))}
          </div>

          {news.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <p>No news updates yet. News will appear here in real-time.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RealTimeData;
