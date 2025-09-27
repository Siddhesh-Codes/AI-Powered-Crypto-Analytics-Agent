import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, BarChart3, Activity, Search, RefreshCw } from 'lucide-react';
import { useMarketStore } from '../store/marketStore';
import { PriceChart, VolumeChart, MarketOverviewChart } from '../components/Charts/ChartComponents';
import { CryptoTable } from '../components/Crypto/CryptoTable';
import { MarketData } from '../services/cryptoAPI';

/**
 * Analytics Page Component
 * Shows detailed crypto analytics, technical indicators, and market insights
 */
const Analytics: React.FC = () => {
  const [selectedCrypto, setSelectedCrypto] = useState<string>('BTC');
  const [timeframe, setTimeframe] = useState<'1h' | '24h' | '7d' | '30d' | '1y'>('24h');
  const [searchQuery, setSearchQuery] = useState('');
  const [watchlist, setWatchlist] = useState<string[]>(['BTC', 'ETH']);

  const {
    topCryptos,
    priceHistory,
    technicalIndicators,
    marketSentiment,
    isLoading,
    fetchTopCryptos,
    fetchPriceHistory,
    fetchTechnicalIndicators,
    fetchMarketSentiment,
    searchCryptos,
    clearPriceHistory,
  } = useMarketStore();

  useEffect(() => {
    // Load initial data with COMPLETE refresh
    const loadData = async () => {
      console.log('🔄 FORCE REFRESHING ALL DATA...');
      
      // Clear ALL existing data
      clearPriceHistory();
      
      // Wait a bit to ensure state is cleared
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Load fresh data
      await fetchTopCryptos(50);
      await fetchTechnicalIndicators(selectedCrypto);
      await fetchMarketSentiment();
      
      console.log('✅ Fresh data loaded');
    };
    loadData();
  }, [fetchTopCryptos, fetchTechnicalIndicators, fetchMarketSentiment, selectedCrypto, clearPriceHistory]);

  useEffect(() => {
    // Force regenerate price history when crypto or timeframe changes
    if (selectedCrypto && topCryptos.length > 0) {
      console.log(`🔄 ANALYTICS: Crypto changed to ${selectedCrypto}, generating fresh price history...`);
      
      // Clear existing data first
      clearPriceHistory();
      
      // Wait a moment then generate fresh data
      setTimeout(() => {
        fetchPriceHistory(selectedCrypto, timeframe);
      }, 100);
    }
  }, [selectedCrypto, timeframe, topCryptos, fetchPriceHistory, clearPriceHistory]);

  // Data consistency check - DISABLED to prevent interference
  // useEffect(() => {
  //   if (selectedCrypto && topCryptos.length > 0) {
  //     const currentCrypto = topCryptos.find(crypto => crypto.symbol === selectedCrypto);
  //     const currentHistory = priceHistory[selectedCrypto];
      
  //     // If we have both current crypto data and price history, ensure they're consistent
  //     if (currentCrypto && currentHistory && currentHistory.length > 0) {
  //       const lastHistoryPrice = currentHistory[currentHistory.length - 1]?.price;
        
  //       if (lastHistoryPrice && currentCrypto.price && currentCrypto.price > 0) {
  //         const priceDifference = Math.abs(lastHistoryPrice - currentCrypto.price) / currentCrypto.price;
          
  //         // If price difference is more than 5%, refresh the price history
  //         if (priceDifference > 0.05) {
  //           console.log(`Price inconsistency detected for ${selectedCrypto}, refreshing...`);
  //           fetchPriceHistory(selectedCrypto, timeframe);
  //         }
  //       }
  //     }
  //   }
  // }, [topCryptos, selectedCrypto, priceHistory, timeframe, fetchPriceHistory]);

  const handleCryptoSelect = (crypto: MarketData) => {
    setSelectedCrypto(crypto.symbol);
    fetchTechnicalIndicators(crypto.symbol);
  };

  const handleToggleWatchlist = (symbol: string) => {
    setWatchlist(prev => 
      prev.includes(symbol) 
        ? prev.filter(s => s !== symbol)
        : [...prev, symbol]
    );
  };

  const handleSearch = async () => {
    if (searchQuery.trim()) {
      await searchCryptos(searchQuery.trim());
    }
  };

  const handleRefresh = async () => {
    console.log('🔄 ANALYTICS REFRESH: Force clearing and regenerating all data...');
    
    // FORCE clear ALL existing data
    clearPriceHistory();
    
    // Wait to ensure state is cleared
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Refresh all base data
    await fetchTopCryptos(50);
    await fetchMarketSentiment();
    
    if (selectedCrypto) {
      await fetchTechnicalIndicators(selectedCrypto);
      
      // Force regenerate price history with fresh data
      await new Promise(resolve => setTimeout(resolve, 100));
      await fetchPriceHistory(selectedCrypto, timeframe);
    }
    
    console.log('✅ ANALYTICS REFRESH: Complete');
  };

  // Get data for selected crypto
  const currentCrypto = topCryptos.find(crypto => crypto.symbol === selectedCrypto);
  const currentPriceHistory = priceHistory[selectedCrypto] || [];
  const currentTechnicalIndicators = technicalIndicators[selectedCrypto];

  // Get the latest price from price history if available for better accuracy
  const latestHistoryPrice = currentPriceHistory.length > 0 
    ? currentPriceHistory[currentPriceHistory.length - 1]?.price 
    : null;
  
  // Use the most recent price data available
  const displayPrice = latestHistoryPrice || currentCrypto?.price || 0;
  const displayCrypto = currentCrypto ? {
    ...currentCrypto,
    price: displayPrice
  } : null;

  // Filter cryptos based on search
  const filteredCryptos = searchQuery 
    ? topCryptos.filter(crypto => 
        crypto.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        crypto.symbol.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : topCryptos;

  // Format technical indicator values
  const formatTechnicalValue = (value: number | undefined, isPercentage = false) => {
    if (value === undefined) return 'N/A';
    return isPercentage ? `${value.toFixed(2)}%` : value.toFixed(2);
  };

  const getTechnicalStatus = (rsi: number | undefined) => {
    if (!rsi) return { label: 'N/A', color: 'text-slate-400' };
    if (rsi > 70) return { label: 'Overbought', color: 'text-red-400' };
    if (rsi < 30) return { label: 'Oversold', color: 'text-green-400' };
    return { label: 'Neutral', color: 'text-yellow-400' };
  };

  const getMACDStatus = (macd: any) => {
    if (!macd) return { label: 'N/A', color: 'text-slate-400' };
    if (macd.trend === 'bullish') return { label: 'Bullish', color: 'text-green-400' };
    if (macd.trend === 'bearish') return { label: 'Bearish', color: 'text-red-400' };
    return { label: 'Neutral', color: 'text-yellow-400' };
  };

  const getSentimentColor = (score: number) => {
    if (score > 0.6) return 'text-green-400';
    if (score < 0.4) return 'text-red-400';
    return 'text-yellow-400';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
        <h1 className="text-3xl font-bold gradient-text">Market Analytics</h1>
        
        {/* Search and Controls */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2">
            <Search className="w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search cryptocurrencies..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="bg-transparent text-white placeholder-slate-400 border-none outline-none w-48"
            />
          </div>
          
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value as any)}
            className="bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2 outline-none"
          >
            <option value="1h">1 Hour</option>
            <option value="24h">24 Hours</option>
            <option value="7d">7 Days</option>
            <option value="30d">30 Days</option>
            <option value="1y">1 Year</option>
          </select>

          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Selected Crypto Overview */}
      {displayCrypto && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <div className="h-12 w-12 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-white font-bold">
                  {displayCrypto.symbol.charAt(0)}
                </span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">{displayCrypto.name}</h2>
                <p className="text-slate-400">{displayCrypto.symbol}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-white">
                ${displayCrypto.price.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: displayCrypto.price < 1 ? 6 : 2,
                })}
              </p>
              <p className={`flex items-center justify-end text-lg ${
                displayCrypto.priceChangePercent24h >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {displayCrypto.priceChangePercent24h >= 0 ? (
                  <TrendingUp className="w-5 h-5 mr-1" />
                ) : (
                  <TrendingDown className="w-5 h-5 mr-1" />
                )}
                {displayCrypto.priceChangePercent24h.toFixed(2)}% (24h)
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Price Chart */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            Price Chart ({timeframe})
          </h2>
          {currentPriceHistory.length > 0 ? (
            <div className="h-80">
              <PriceChart
                data={currentPriceHistory}
                symbol={selectedCrypto}
                timeframe={timeframe}
                className="h-full"
              />
            </div>
          ) : (
            <div className="h-80 flex items-center justify-center text-slate-400">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Loading chart data...</p>
              </div>
            </div>
          )}
        </div>

        {/* Volume Chart */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            Volume Chart
          </h2>
          {currentPriceHistory.length > 0 ? (
            <div className="h-80">
              <VolumeChart
                data={currentPriceHistory}
                symbol={selectedCrypto}
                className="h-full"
              />
            </div>
          ) : (
            <div className="h-80 flex items-center justify-center text-slate-400">
              <div className="text-center">
                <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Loading volume data...</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Technical Indicators & Market Sentiment */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Technical Indicators */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Technical Indicators</h2>
          <div className="space-y-4">
            {/* RSI */}
            <div className="flex justify-between items-center">
              <div>
                <span className="text-slate-300">RSI (14)</span>
                <p className="text-xs text-slate-500">Relative Strength Index</p>
              </div>
              <div className="text-right">
                <span className="text-white font-medium">
                  {formatTechnicalValue(currentTechnicalIndicators?.rsi)}
                </span>
                <p className={`text-xs ${getTechnicalStatus(currentTechnicalIndicators?.rsi).color}`}>
                  {getTechnicalStatus(currentTechnicalIndicators?.rsi).label}
                </p>
              </div>
            </div>

            {/* MACD */}
            <div className="flex justify-between items-center">
              <div>
                <span className="text-slate-300">MACD</span>
                <p className="text-xs text-slate-500">Moving Average Convergence Divergence</p>
              </div>
              <div className="text-right">
                <span className="text-white font-medium">
                  {formatTechnicalValue(currentTechnicalIndicators?.macd?.macd)}
                </span>
                <p className={`text-xs ${getMACDStatus(currentTechnicalIndicators?.macd).color}`}>
                  {getMACDStatus(currentTechnicalIndicators?.macd).label}
                </p>
              </div>
            </div>

            {/* Bollinger Bands */}
            <div className="flex justify-between items-center">
              <div>
                <span className="text-slate-300">Bollinger Bands</span>
                <p className="text-xs text-slate-500">Price position relative to bands</p>
              </div>
              <div className="text-right">
                <span className="text-white font-medium">
                  {currentTechnicalIndicators?.bollingerBands?.position || 'N/A'}
                </span>
                <p className="text-xs text-blue-400">Middle Band</p>
              </div>
            </div>

            {/* Moving Averages */}
            <div className="pt-4 border-t border-slate-700">
              <h4 className="text-sm font-medium text-slate-300 mb-2">Moving Averages</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">SMA 20</span>
                  <span className="text-white">
                    ${formatTechnicalValue(currentTechnicalIndicators?.movingAverages?.sma20)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">EMA 20</span>
                  <span className="text-white">
                    ${formatTechnicalValue(currentTechnicalIndicators?.movingAverages?.ema20)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">SMA 50</span>
                  <span className="text-white">
                    ${formatTechnicalValue(currentTechnicalIndicators?.movingAverages?.sma50)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">EMA 50</span>
                  <span className="text-white">
                    ${formatTechnicalValue(currentTechnicalIndicators?.movingAverages?.ema50)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Market Sentiment */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Market Sentiment</h2>
          <div className="space-y-4">
            {/* Twitter Sentiment */}
            <div className="flex justify-between items-center">
              <div>
                <span className="text-slate-300">Twitter Sentiment</span>
                <p className="text-xs text-slate-500">
                  {marketSentiment?.twitterSentiment?.mentions?.toLocaleString() || 0} mentions
                </p>
              </div>
              <div className="text-right">
                <span className={`font-medium capitalize ${
                  getSentimentColor(marketSentiment?.twitterSentiment?.score || 0.5)
                }`}>
                  {marketSentiment?.twitterSentiment?.label || 'Neutral'}
                </span>
                <p className="text-xs text-slate-400">
                  {((marketSentiment?.twitterSentiment?.score || 0.5) * 100).toFixed(0)}%
                </p>
              </div>
            </div>

            {/* News Sentiment */}
            <div className="flex justify-between items-center">
              <div>
                <span className="text-slate-300">News Sentiment</span>
                <p className="text-xs text-slate-500">
                  {marketSentiment?.newsSentiment?.articles || 0} articles analyzed
                </p>
              </div>
              <div className="text-right">
                <span className={`font-medium capitalize ${
                  getSentimentColor(marketSentiment?.newsSentiment?.score || 0.5)
                }`}>
                  {marketSentiment?.newsSentiment?.label || 'Neutral'}
                </span>
                <p className="text-xs text-slate-400">
                  {((marketSentiment?.newsSentiment?.score || 0.5) * 100).toFixed(0)}%
                </p>
              </div>
            </div>

            {/* Social Volume */}
            <div className="flex justify-between items-center">
              <div>
                <span className="text-slate-300">Social Volume</span>
                <p className="text-xs text-slate-500">
                  {marketSentiment?.socialVolume?.change24h !== undefined 
                    ? `${marketSentiment.socialVolume.change24h >= 0 ? '+' : ''}${marketSentiment.socialVolume.change24h.toFixed(1)}% (24h)`
                    : 'N/A (24h)'
                  }
                </p>
              </div>
              <div className="text-right">
                <span className={`font-medium capitalize ${
                  marketSentiment?.socialVolume?.label === 'high' ? 'text-green-400' :
                  marketSentiment?.socialVolume?.label === 'low' ? 'text-red-400' : 'text-yellow-400'
                }`}>
                  {marketSentiment?.socialVolume?.label || 'Medium'}
                </span>
                <p className="text-xs text-slate-400">Activity Level</p>
              </div>
            </div>

            {/* Reddit Sentiment */}
            <div className="flex justify-between items-center">
              <div>
                <span className="text-slate-300">Reddit Sentiment</span>
                <p className="text-xs text-slate-500">
                  {marketSentiment?.redditSentiment?.posts?.toLocaleString() || 0} posts
                </p>
              </div>
              <div className="text-right">
                <span className={`font-medium capitalize ${
                  getSentimentColor(marketSentiment?.redditSentiment?.score || 0.5)
                }`}>
                  {marketSentiment?.redditSentiment?.label || 'Neutral'}
                </span>
                <p className="text-xs text-slate-400">
                  {((marketSentiment?.redditSentiment?.score || 0.5) * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Cryptocurrency Table */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">
            {searchQuery ? 'Search Results' : 'All Cryptocurrencies'}
          </h2>
          <button
            onClick={() => {
              fetchTopCryptos(50);
              fetchMarketSentiment();
            }}
            disabled={isLoading}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
        
        <CryptoTable
          data={filteredCryptos}
          onCryptoSelect={handleCryptoSelect}
          watchlist={watchlist}
          onToggleWatchlist={handleToggleWatchlist}
        />
      </div>
    </div>
  );
};

export default Analytics;
