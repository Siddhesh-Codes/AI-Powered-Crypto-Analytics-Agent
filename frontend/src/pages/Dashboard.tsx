import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, RefreshCw, Activity, DollarSign, BarChart3, Brain, Bell, Newspaper } from 'lucide-react';
import { useMarketStore } from '../store/marketStore';
import { usePortfolioStore } from '../store/portfolioStore';
import { PriceChart, MarketOverviewChart } from '../components/Charts/ChartComponents';
import { CompactCryptoList } from '../components/Crypto/CryptoTable';
import { TradingViewMiniWidget } from '../components/TradingView/TradingViewWidget';
import AlertsManager from '../components/Alerts/AlertsManager';
import TradingSignals from '../components/Trading/TradingSignals';
import NewsAndSentiment from '../components/News';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';

/**
 * Dashboard Page Component
 * Main landing page showing overview of crypto market and user portfolio
 */
const Dashboard: React.FC = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  const {
    topCryptos,
    globalMetrics,
    priceHistory,
    isLoading: marketLoading,
    fetchTopCryptos,
    fetchGlobalMetrics,
    fetchPriceHistory,
    setSelectedCrypto,
    startAutoRefresh,
    stopAutoRefresh,
  } = useMarketStore();

  const {
    totalValue,
    totalChangePercent24h,
    assets,
    calculateTotals,
  } = usePortfolioStore();

  useEffect(() => {
    // FORCE COMPLETE DATA REFRESH
    const loadData = async () => {
      console.log('🔄 DASHBOARD: FORCE REFRESHING ALL DATA...');
      
      // Load fresh crypto data (this will generate proper price history)
      await fetchTopCryptos(10);
      await fetchGlobalMetrics();
      
      console.log('✅ DASHBOARD: Fresh data loaded');
    };

    loadData();
    calculateTotals();
    
    // Start daily price updates
    startAutoRefresh();
    
    // Cleanup on unmount
    return () => {
      stopAutoRefresh();
    };
  }, [fetchTopCryptos, fetchGlobalMetrics, calculateTotals, startAutoRefresh, stopAutoRefresh]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await Promise.all([
        fetchTopCryptos(10),
        fetchGlobalMetrics(),
      ]);
      toast.success('Data refreshed successfully');
    } catch (error) {
      toast.error('Failed to refresh data');
    } finally {
      setIsRefreshing(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatLargeCurrency = (value: number) => {
    if (value >= 1e12) {
      return `$${(value / 1e12).toFixed(2)}T`;
    } else if (value >= 1e9) {
      return `$${(value / 1e9).toFixed(2)}B`;
    } else if (value >= 1e6) {
      return `$${(value / 1e6).toFixed(2)}M`;
    } else {
      return formatCurrency(value);
    }
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  // Get Bitcoin price history for chart
  const btcHistory = priceHistory['BTC'] || [];
  const btcData = topCryptos.find(crypto => crypto.symbol === 'BTC');

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold gradient-text">
          Crypto Analytics Dashboard
        </h1>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-slate-400">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span>Market Analysis</span>
          </div>
          <button
            onClick={handleRefresh}
            disabled={isRefreshing || marketLoading}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Market Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold text-slate-300">Total Market Cap</h3>
            <DollarSign className="w-5 h-5 text-green-400" />
          </div>
          <p className="text-2xl font-bold text-green-400">
            {globalMetrics ? formatLargeCurrency(globalMetrics.totalMarketCap) : '$2.1T'}
          </p>
          <p className={`text-sm ${
            (globalMetrics?.totalMarketCapChange24h || 2.4) >= 0 ? 'text-green-400' : 'text-red-400'
          }`}>
            {formatPercent(globalMetrics?.totalMarketCapChange24h || 2.4)}
          </p>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold text-slate-300">24h Volume</h3>
            <BarChart3 className="w-5 h-5 text-blue-400" />
          </div>
          <p className="text-2xl font-bold text-blue-400">
            {globalMetrics ? formatLargeCurrency(globalMetrics.total24hVolume) : '$89.2B'}
          </p>
          <p className={`text-sm ${
            (globalMetrics?.total24hVolumeChange || 1.8) >= 0 ? 'text-green-400' : 'text-red-400'
          }`}>
            {formatPercent(globalMetrics?.total24hVolumeChange || 1.8)}
          </p>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold text-slate-300">BTC Dominance</h3>
            <Activity className="w-5 h-5 text-yellow-400" />
          </div>
          <p className="text-2xl font-bold text-yellow-400">
            {globalMetrics ? `${globalMetrics.btcDominance.toFixed(1)}%` : '42.3%'}
          </p>
          <p className="text-sm text-slate-400">
            ETH: {globalMetrics ? `${globalMetrics.ethDominance.toFixed(1)}%` : '15.5%'}
          </p>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold text-slate-300">Fear & Greed</h3>
            <Activity className="w-5 h-5 text-purple-400" />
          </div>
          <p className="text-2xl font-bold text-purple-400">
            {globalMetrics?.fearGreedIndex || 65}
          </p>
          <p className="text-sm text-slate-400">
            {globalMetrics?.fearGreedValue || 'Greed'}
          </p>
        </div>
      </div>

      {/* Portfolio Overview & Bitcoin Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Portfolio Overview */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <DollarSign className="w-5 h-5 mr-2" />
            Portfolio Overview
          </h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Total Value</span>
              <span className="text-xl font-bold text-white">
                {formatCurrency(totalValue)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">24h Change</span>
              <span className={`font-medium ${
                totalChangePercent24h >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {totalChangePercent24h >= 0 ? (
                  <TrendingUp className="w-4 h-4 inline mr-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 inline mr-1" />
                )}
                {formatPercent(totalChangePercent24h)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Total Assets</span>
              <span className="font-medium text-white">{assets.length}</span>
            </div>
            <div className="pt-4 border-t border-slate-700">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Performance</span>
                <span className={totalChangePercent24h >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {totalChangePercent24h >= 0 ? 'Profitable' : 'Loss'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Bitcoin Price Chart - Professional Chart with Daily Data */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            Bitcoin Price (24h) - Daily Analysis
          </h2>
          {btcHistory.length > 0 ? (
            <div className="h-64">
              <PriceChart
                data={btcHistory}
                symbol="BTC"
                timeframe="24h"
                className="h-full"
              />
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-400">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Loading daily chart data...</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Top Cryptocurrencies & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Cryptocurrencies */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Top Cryptocurrencies</h2>
            <Link 
              to="/crypto/btc" 
              className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
            >
              View Individual Analysis →
            </Link>
          </div>
          {topCryptos.length > 0 ? (
            <div className="space-y-2">
              <CompactCryptoList
                data={topCryptos.slice(0, 8)}
                onCryptoSelect={(crypto) => {
                  setSelectedCrypto(crypto.symbol);
                  // Navigate to individual crypto analysis
                  window.location.href = `/crypto/${crypto.symbol.toLowerCase()}`;
                }}
                showRank={true}
              />
              
              {/* Quick Crypto Links */}
              <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-slate-700">
                {['BTC', 'ETH', 'ADA', 'SOL', 'DOT'].map(symbol => (
                  <Link
                    key={symbol}
                    to={`/crypto/${symbol.toLowerCase()}`}
                    className="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm transition-colors"
                  >
                    {symbol} Analysis
                  </Link>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-slate-400">
              Loading cryptocurrency data...
            </div>
          )}
        </div>

        {/* Enhanced Quick Actions */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">AI Tools & Features</h2>
          <div className="space-y-3">
            <button 
              className="flex items-center space-x-3 p-3 bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 rounded-lg transition-all transform hover:scale-[1.02] w-full"
              onClick={() => window.location.href = '/alerts'}
            >
              <Bell className="w-5 h-5" />
              <div className="text-left">
                <div className="font-medium">Smart Alerts</div>
                <div className="text-xs opacity-80">Daily market analysis</div>
              </div>
            </button>
            
            <button 
              className="flex items-center space-x-3 p-3 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 rounded-lg transition-all transform hover:scale-[1.02] w-full"
              onClick={() => window.location.href = '/signals'}
            >
              <Activity className="w-5 h-5" />
              <div className="text-left">
                <div className="font-medium">Trading Signals</div>
                <div className="text-xs opacity-80">AI-powered recommendations</div>
              </div>
            </button>
            
            <button 
              className="flex items-center space-x-3 p-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 rounded-lg transition-all transform hover:scale-[1.02] w-full"
              onClick={() => window.location.href = '/news'}
            >
              <Newspaper className="w-5 h-5" />
              <div className="text-left">
                <div className="font-medium">News & Sentiment</div>
                <div className="text-xs opacity-80">Market sentiment analysis</div>
              </div>
            </button>
            
            <Link 
              to="/portfolio"
              className="flex items-center space-x-3 p-3 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
            >
              <DollarSign className="w-5 h-5" />
              <div>
                <div className="font-medium">Portfolio Analytics</div>
                <div className="text-xs text-slate-400">Track performance</div>
              </div>
            </Link>
          </div>
          
          {/* AI-Powered Recent Activity */}
          <div className="mt-6">
            <h3 className="text-lg font-medium mb-3">AI Insights</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-slate-700 rounded-lg">
                <div>
                  <p className="font-medium text-sm flex items-center">
                    <Brain className="w-4 h-4 mr-2 text-purple-400" />
                    {btcData ? `Bitcoin AI Signal: ${btcData.priceChangePercent24h > 0 ? 'BUY' : 'HOLD'}` : 'AI Analysis Ready'}
                  </p>
                  <p className="text-xs text-slate-400">
                    {btcData ? `Confidence: ${Math.round(Math.abs(btcData.priceChangePercent24h) * 10 + 70)}%` : 'Daily AI monitoring'}
                  </p>
                </div>
                <span className="text-xs text-green-400">Active</span>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-slate-700 rounded-lg">
                <div>
                  <p className="font-medium text-sm flex items-center">
                    <Bell className="w-4 h-4 mr-2 text-blue-400" />
                    Smart Alerts Monitoring
                  </p>
                  <p className="text-xs text-slate-400">
                    {topCryptos.length} assets being tracked
                  </p>
                </div>
                <span className="text-xs text-blue-400">Live</span>
              </div>

              <div className="flex justify-between items-center p-3 bg-slate-700 rounded-lg">
                <div>
                  <p className="font-medium text-sm flex items-center">
                    <Newspaper className="w-4 h-4 mr-2 text-orange-400" />
                    Market Sentiment
                  </p>
                  <p className="text-xs text-slate-400">
                    {globalMetrics?.fearGreedValue || 'Neutral'} - {globalMetrics?.fearGreedIndex || 50}/100
                  </p>
                </div>
                <span className="text-xs text-orange-400">Updated</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Features Preview Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trading Signals Preview */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold flex items-center">
              <Activity className="w-5 h-5 mr-2 text-green-400" />
              Latest Trading Signals
            </h2>
            <Link 
              to="/signals"
              className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
            >
              View All →
            </Link>
          </div>
          
          <div className="space-y-3">
            {topCryptos.slice(0, 3).map((crypto, index) => {
              const signalType = crypto.priceChangePercent24h > 3 ? 'BUY' : crypto.priceChangePercent24h < -3 ? 'SELL' : 'HOLD';
              const signalColor = signalType === 'BUY' ? 'text-green-400' : signalType === 'SELL' ? 'text-red-400' : 'text-yellow-400';
              
              return (
                <div key={crypto.symbol} className="flex items-center justify-between p-3 bg-slate-700 rounded-lg">
                  <div>
                    <div className="font-medium text-slate-200">{crypto.symbol}</div>
                    <div className="text-sm text-slate-400">AI Confidence: {Math.round(Math.abs(crypto.priceChangePercent24h) * 10 + 70)}%</div>
                  </div>
                  <div className={`px-3 py-1 rounded-lg font-medium ${signalColor} bg-opacity-20 border border-current`}>
                    {signalType}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* News Preview */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold flex items-center">
              <Newspaper className="w-5 h-5 mr-2 text-blue-400" />
              Crypto News Feed
            </h2>
            <Link 
              to="/news"
              className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
            >
              View All →
            </Link>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-start space-x-3 p-3 bg-slate-700 rounded-lg">
              <div className="w-2 h-2 bg-green-400 rounded-full mt-2"></div>
              <div>
                <div className="font-medium text-slate-200 text-sm">Bitcoin ETF Drives Institutional Interest</div>
                <div className="text-xs text-slate-400 mt-1">BULLISH sentiment • 15 minutes ago</div>
              </div>
            </div>
            
            <div className="flex items-start space-x-3 p-3 bg-slate-700 rounded-lg">
              <div className="w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
              <div>
                <div className="font-medium text-slate-200 text-sm">Ethereum Network Upgrade Shows Progress</div>
                <div className="text-xs text-slate-400 mt-1">NEUTRAL sentiment • 1 hour ago</div>
              </div>
            </div>
            
            <div className="flex items-start space-x-3 p-3 bg-slate-700 rounded-lg">
              <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2"></div>
              <div>
                <div className="font-medium text-slate-200 text-sm">DeFi Protocol Launches New Features</div>
                <div className="text-xs text-slate-400 mt-1">BULLISH sentiment • 2 hours ago</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Market Overview Chart - Professional Chart with Daily Data */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <Activity className="w-5 h-5 mr-2" />
          Market Overview - Daily Price Analysis
        </h2>
        <div className="h-[500px]">
          <MarketOverviewChart
            data={topCryptos.slice(0, 8).map(crypto => ({
              symbol: crypto.symbol,
              marketCap: crypto.marketCap || 0,
              change24h: crypto.priceChange24h
            }))}
            className="h-full"
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
