import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { AIChatbot } from '../components/AI/AIChatbot';
import { TradingViewWidget } from '../components/TradingView/TradingViewWidget';
import { PriceChart } from '../components/Charts/ChartComponents';
import { useMarketStore } from '../store/marketStore';
import ErrorBoundary from '../components/ErrorBoundary';
import { TrendingUp, TrendingDown, Activity, Brain, BarChart3 } from 'lucide-react';

/**
 * Individual Crypto Analysis Page with Dedicated AI Chat
 */
const CryptoAnalysis: React.FC = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const [chatOpen, setChatOpen] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { topCryptos, priceHistory, fetchPriceHistory } = useMarketStore();
  
  const crypto = topCryptos.find(c => c?.symbol?.toLowerCase() === symbol?.toLowerCase());
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        if (symbol) {
          await fetchPriceHistory(symbol.toUpperCase(), '7d');
        }
      } catch (err) {
        console.error('Error fetching price history:', err);
        setError('Failed to load price history data');
      }
    };

    fetchData();
  }, [symbol, fetchPriceHistory]);

  // Error boundary for runtime errors
  if (error) {
    return (
      <div className="p-6 text-center">
        <h1 className="text-2xl font-bold text-red-400">Error Loading Analysis</h1>
        <p className="text-slate-500">{error}</p>
        <button 
          onClick={() => {
            setError(null);
            window.location.reload();
          }}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  // Loading state while crypto data is being fetched
  if (!symbol) {
    return (
      <div className="p-6 text-center">
        <h1 className="text-2xl font-bold text-slate-300">Invalid URL</h1>
        <p className="text-slate-500">No cryptocurrency symbol provided.</p>
      </div>
    );
  }

  if (!crypto && topCryptos.length === 0) {
    return (
      <div className="p-6 text-center">
        <h1 className="text-2xl font-bold text-slate-300">Loading...</h1>
        <p className="text-slate-500">Fetching cryptocurrency data...</p>
      </div>
    );
  }

  if (!crypto) {
    return (
      <div className="p-6 text-center">
        <h1 className="text-2xl font-bold text-slate-300">Cryptocurrency not found</h1>
        <p className="text-slate-500">The cryptocurrency {symbol.toUpperCase()} was not found in our database.</p>
        <p className="text-slate-400 mt-2">Available symbols: {topCryptos.slice(0, 5).map(c => c.symbol).join(', ')}</p>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-lg">{crypto.symbol}</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold gradient-text">{crypto.name} Analysis</h1>
              <p className="text-slate-400">AI-Powered {crypto.symbol} Intelligence</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-2xl font-bold">${crypto.price?.toLocaleString()}</div>
              <div className={`flex items-center ${crypto.priceChangePercent24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {crypto.priceChangePercent24h >= 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
                {crypto.priceChangePercent24h?.toFixed(2)}%
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          
          {/* Charts and Data - Left Side */}
          <div className="xl:col-span-2 space-y-6">
            
            {/* TradingView Chart */}
            <div className="card chart-container">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2 text-blue-400" />
                  {crypto.symbol} Professional Chart
                </h2>
                <div className="flex space-x-2">
                  <span className="px-3 py-1 bg-blue-600 text-white rounded-lg text-sm">Live</span>
                  <span className="px-3 py-1 bg-slate-700 text-slate-300 rounded-lg text-sm">Advanced</span>
                </div>
              </div>
              <div className="h-[600px] w-full">
                <ErrorBoundary fallback={
                  <div className="flex items-center justify-center h-full bg-slate-700 rounded">
                    <p className="text-slate-400">Chart temporarily unavailable</p>
                  </div>
                }>
                  <TradingViewWidget 
                    symbol={`${crypto.symbol}USD`} 
                    height="600"
                    width="100%"
                  />
                </ErrorBoundary>
              </div>
            </div>

            {/* Market Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="card text-center">
                <div className="text-sm text-slate-400">Market Cap</div>
                <div className="text-lg font-bold">${((crypto.marketCap || 0) / 1e9).toFixed(2)}B</div>
              </div>
              <div className="card text-center">
                <div className="text-sm text-slate-400">24h Volume</div>
                <div className="text-lg font-bold">${((crypto.volume24h || 0) / 1e9).toFixed(2)}B</div>
              </div>
              <div className="card text-center">
                <div className="text-sm text-slate-400">Circulating Supply</div>
                <div className="text-lg font-bold">{((crypto.circulatingSupply || 0) / 1e6).toFixed(2)}M</div>
              </div>
              <div className="card text-center">
                <div className="text-sm text-slate-400">Market Rank</div>
                <div className="text-lg font-bold">#{crypto.rank || 'N/A'}</div>
              </div>
            </div>
          </div>

          {/* AI Chat - Right Side */}
          <div className="xl:col-span-1">
            <div className="card h-full">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold flex items-center">
                  <Brain className="w-5 h-5 mr-2 text-green-400" />
                  {crypto.symbol} AI Assistant
                </h2>
                <button
                  onClick={() => setChatOpen(!chatOpen)}
                  className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
                >
                  <Activity className="w-4 h-4" />
                </button>
              </div>
              
              {chatOpen && (
                <div className="h-96">
                  {(() => {
                    try {
                      return (
                        <AIChatbot 
                          isOpen={true}
                          onToggle={() => setChatOpen(!chatOpen)}
                          className="relative"
                          cryptoContext={{
                            symbol: crypto.symbol,
                            name: crypto.name,
                            price: crypto.price || 0,
                            change24h: crypto.priceChangePercent24h || 0,
                            marketCap: crypto.marketCap || 0,
                            volume: crypto.volume24h || 0
                          }}
                        />
                      );
                    } catch (err) {
                      console.error('AI Chatbot error:', err);
                      return (
                        <div className="p-4 text-center">
                          <p className="text-red-400">AI Chat temporarily unavailable</p>
                          <button 
                            onClick={() => window.location.reload()}
                            className="mt-2 px-3 py-1 bg-blue-600 text-white rounded text-sm"
                          >
                            Reload
                          </button>
                        </div>
                      );
                    }
                  })()}
                </div>
              )}
              
              {/* Quick Analysis Buttons */}
              <div className="mt-4 space-y-2">
                <button className="w-full p-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition-colors">
                  📊 Technical Analysis
                </button>
                <button className="w-full p-3 bg-green-600 hover:bg-green-700 rounded-lg text-white transition-colors">
                  💰 Investment Advice
                </button>
                <button className="w-full p-3 bg-purple-600 hover:bg-purple-700 rounded-lg text-white transition-colors">
                  🔮 Price Prediction
                </button>
                <button className="w-full p-3 bg-orange-600 hover:bg-orange-700 rounded-lg text-white transition-colors">
                  ⚠️ Risk Analysis
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default CryptoAnalysis;
