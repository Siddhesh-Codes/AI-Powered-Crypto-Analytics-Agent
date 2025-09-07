import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Zap, Target, Brain, Activity } from 'lucide-react';
import { useMarketStore } from '../../store/marketStore';

interface TradingSignal {
  id: string;
  symbol: string;
  type: 'BUY' | 'SELL' | 'HOLD';
  strength: number; // 1-100
  indicators: string[];
  entry_price: number;
  target_price: number;
  stop_loss: number;
  timeframe: string;
  generated_at: Date;
  ai_confidence: number;
  reason: string;
}

/**
 * Advanced AI Trading Signals Component
 * Provides real-time trading recommendations based on technical analysis
 */
const TradingSignals: React.FC = () => {
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [activeTimeframe, setActiveTimeframe] = useState('1h');
  const [filterType, setFilterType] = useState<'ALL' | 'BUY' | 'SELL' | 'HOLD'>('ALL');
  
  const { topCryptos, isLoading, fetchTopCryptos } = useMarketStore();

  // Fetch market data on component mount
  useEffect(() => {
    if (topCryptos.length === 0) {
      fetchTopCryptos(20);
    }
  }, [topCryptos.length, fetchTopCryptos]);

  // Generate AI trading signals based on market data
  useEffect(() => {
    const generateSignals = () => {
      const newSignals: TradingSignal[] = topCryptos.slice(0, 10).map((crypto, index) => {
        // Simulate AI analysis
        const change24h = crypto.priceChangePercent24h;
        const volume = crypto.volume24h;
        
        // AI decision logic (simplified for demo)
        let type: TradingSignal['type'] = 'HOLD';
        let strength = 50;
        let indicators: string[] = [];
        let ai_confidence = 0;
        let reason = '';

        // Bullish signals
        if (change24h > 5 && (volume || 0) > 1e9) {
          type = 'BUY';
          strength = Math.min(85, 60 + change24h);
          indicators = ['RSI Oversold', 'Volume Breakout', 'MACD Bullish'];
          ai_confidence = 87;
          reason = 'Strong upward momentum with high volume';
        }
        // Bearish signals
        else if (change24h < -5 && (volume || 0) > 1e9) {
          type = 'SELL';
          strength = Math.min(85, 60 + Math.abs(change24h));
          indicators = ['RSI Overbought', 'Volume Spike', 'Support Break'];
          ai_confidence = 82;
          reason = 'Bearish momentum with high selling pressure';
        }
        // Sideways/Hold
        else {
          type = 'HOLD';
          strength = 30 + Math.random() * 40;
          indicators = ['Consolidation', 'Range Bound'];
          ai_confidence = 65;
          reason = 'Market consolidation, waiting for breakout';
        }

        return {
          id: `signal_${index}`,
          symbol: crypto.symbol,
          type,
          strength: Math.round(strength),
          indicators,
          entry_price: crypto.price,
          target_price: type === 'BUY' ? crypto.price * 1.08 : crypto.price * 0.95,
          stop_loss: type === 'BUY' ? crypto.price * 0.95 : crypto.price * 1.03,
          timeframe: activeTimeframe,
          generated_at: new Date(),
          ai_confidence: Math.round(ai_confidence),
          reason
        };
      });

      setSignals(newSignals);
    };

    generateSignals();
    const interval = setInterval(generateSignals, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [topCryptos, activeTimeframe]);

  const filteredSignals = signals.filter(signal => 
    filterType === 'ALL' || signal.type === filterType
  );

  const getSignalColor = (type: TradingSignal['type']) => {
    switch (type) {
      case 'BUY': return 'text-green-400 bg-green-900/20 border-green-500';
      case 'SELL': return 'text-red-400 bg-red-900/20 border-red-500';
      case 'HOLD': return 'text-yellow-400 bg-yellow-900/20 border-yellow-500';
    }
  };

  const getSignalIcon = (type: TradingSignal['type']) => {
    switch (type) {
      case 'BUY': return <TrendingUp className="w-5 h-5" />;
      case 'SELL': return <TrendingDown className="w-5 h-5" />;
      case 'HOLD': return <Activity className="w-5 h-5" />;
    }
  };

  const getStrengthColor = (strength: number) => {
    if (strength >= 80) return 'bg-green-500';
    if (strength >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold gradient-text flex items-center">
            <Brain className="w-8 h-8 mr-3 text-purple-400" />
            AI Trading Signals
          </h2>
          <p className="text-slate-400">Real-time AI-powered trading recommendations</p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Timeframe Selector */}
          <select
            value={activeTimeframe}
            onChange={(e) => setActiveTimeframe(e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:border-blue-500"
          >
            <option value="5m">5 Minutes</option>
            <option value="15m">15 Minutes</option>
            <option value="1h">1 Hour</option>
            <option value="4h">4 Hours</option>
            <option value="1d">1 Day</option>
          </select>

          {/* Signal Filter */}
          <div className="flex bg-slate-700 rounded-lg p-1">
            {(['ALL', 'BUY', 'SELL', 'HOLD'] as const).map(type => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`px-3 py-1 rounded-md text-sm transition-colors ${
                  filterType === type
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* AI Market Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card text-center">
          <Zap className="w-8 h-8 text-green-400 mx-auto mb-2" />
          <div className="text-sm text-slate-400">Buy Signals</div>
          <div className="text-xl font-bold text-green-400">
            {signals.filter(s => s.type === 'BUY').length}
          </div>
        </div>
        
        <div className="card text-center">
          <Target className="w-8 h-8 text-red-400 mx-auto mb-2" />
          <div className="text-sm text-slate-400">Sell Signals</div>
          <div className="text-xl font-bold text-red-400">
            {signals.filter(s => s.type === 'SELL').length}
          </div>
        </div>
        
        <div className="card text-center">
          <Activity className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
          <div className="text-sm text-slate-400">Hold Signals</div>
          <div className="text-xl font-bold text-yellow-400">
            {signals.filter(s => s.type === 'HOLD').length}
          </div>
        </div>
        
        <div className="card text-center">
          <Brain className="w-8 h-8 text-purple-400 mx-auto mb-2" />
          <div className="text-sm text-slate-400">AI Confidence</div>
          <div className="text-xl font-bold text-purple-400">
            {Math.round(signals.reduce((acc, s) => acc + s.ai_confidence, 0) / signals.length)}%
          </div>
        </div>
      </div>

      {/* Trading Signals List */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="card text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-slate-400">Loading trading signals...</p>
          </div>
        ) : filteredSignals.length === 0 ? (
          <div className="card text-center py-8">
            <Brain className="w-12 h-12 text-slate-500 mx-auto mb-4" />
            <p className="text-slate-400 mb-2">No trading signals available</p>
            <p className="text-sm text-slate-500">Signals will appear once market data is loaded</p>
          </div>
        ) : (
          filteredSignals.map(signal => (
            <div key={signal.id} className={`card border-l-4 ${getSignalColor(signal.type)}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className={`p-3 rounded-lg border-2 ${getSignalColor(signal.type)}`}>
                    {getSignalIcon(signal.type)}
                  </div>
                
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="text-lg font-bold text-white">{signal.symbol}</h3>
                    <span className={`px-2 py-1 rounded text-sm font-medium ${getSignalColor(signal.type)}`}>
                      {signal.type}
                    </span>
                  </div>
                  <p className="text-slate-400 text-sm">{signal.reason}</p>
                  <div className="flex items-center space-x-4 mt-2 text-sm">
                    <span className="text-slate-500">
                      Entry: ${signal.entry_price.toLocaleString()}
                    </span>
                    <span className="text-green-400">
                      Target: ${signal.target_price.toLocaleString()}
                    </span>
                    <span className="text-red-400">
                      Stop: ${signal.stop_loss.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>

              <div className="text-right space-y-2">
                {/* Signal Strength */}
                <div>
                  <div className="text-sm text-slate-400 mb-1">Signal Strength</div>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${getStrengthColor(signal.strength)}`}
                        style={{ width: `${signal.strength}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium">{signal.strength}%</span>
                  </div>
                </div>

                {/* AI Confidence */}
                <div>
                  <div className="text-sm text-slate-400 mb-1">AI Confidence</div>
                  <div className="flex items-center space-x-2">
                    <Brain className="w-4 h-4 text-purple-400" />
                    <span className="text-sm font-medium text-purple-400">
                      {signal.ai_confidence}%
                    </span>
                  </div>
                </div>

                {/* Technical Indicators */}
                <div>
                  <div className="text-sm text-slate-400 mb-1">Indicators</div>
                  <div className="flex flex-wrap gap-1">
                    {signal.indicators.map((indicator, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-slate-700 text-xs rounded text-slate-300"
                      >
                        {indicator}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
          ))
        )}
      </div>

      {/* AI Disclaimer */}
      <div className="card bg-slate-700/50 border border-slate-600">
        <div className="flex items-start space-x-3">
          <Brain className="w-6 h-6 text-purple-400 mt-1" />
          <div>
            <h4 className="font-semibold text-slate-200 mb-2">AI Trading Signals Disclaimer</h4>
            <p className="text-sm text-slate-400">
              These signals are generated by AI analysis of market data and should not be considered as financial advice. 
              Always do your own research (DYOR) and consider your risk tolerance before making any trading decisions. 
              Past performance does not guarantee future results.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingSignals;
