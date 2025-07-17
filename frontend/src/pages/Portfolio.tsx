import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  TrendingUp, 
  TrendingDown, 
  RefreshCw, 
  Settings, 
  Eye, 
  EyeOff,
  ExternalLink,
  Edit,
  Trash2,
  DollarSign,
  BarChart3,
  PieChart
} from 'lucide-react';
import { usePortfolioStore } from '../store/portfolioStore';
import { useMarketStore } from '../store/marketStore';
import { PortfolioChart, PriceChart } from '../components/Charts/ChartComponents';
import toast from 'react-hot-toast';

/**
 * Portfolio Page Component
 * Comprehensive portfolio management with exchange integration
 */
const Portfolio: React.FC = () => {
  const [showValues, setShowValues] = useState(true);
  const [showAddAsset, setShowAddAsset] = useState(false);
  const [showConnectExchange, setShowConnectExchange] = useState(false);
  
  const {
    assets,
    exchanges,
    totalValue,
    totalChange24h,
    totalChangePercent24h,
    isLoading,
    addAsset,
    updateAsset,
    removeAsset,
    addExchange,
    syncExchange,
    calculateTotals,
    refreshPrices
  } = usePortfolioStore();

  useEffect(() => {
    calculateTotals();
  }, [calculateTotals]);

  const formatCurrency = (value: number) => {
    if (!showValues) return '***';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">Portfolio</h1>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowValues(!showValues)}
            className="p-2 text-slate-400 hover:text-white transition-colors"
            title={showValues ? "Hide values" : "Show values"}
          >
            {showValues ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
          </button>
          <button
            onClick={refreshPrices}
            disabled={isLoading}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => setShowConnectExchange(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
            <span>Connect Exchange</span>
          </button>
          <button
            onClick={() => setShowAddAsset(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Asset</span>
          </button>
        </div>
      </div>

      {/* Portfolio Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-slate-400 text-sm">Total Portfolio Value</h3>
            <DollarSign className="w-4 h-4 text-slate-400" />
          </div>
          <p className="text-2xl font-bold text-white">{formatCurrency(totalValue)}</p>
        </div>
        
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-slate-400 text-sm">24h Change</h3>
            {totalChangePercent24h >= 0 ? (
              <TrendingUp className="w-4 h-4 text-green-400" />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-400" />
            )}
          </div>
          <p className={`text-2xl font-bold ${totalChangePercent24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {showValues ? formatPercent(totalChangePercent24h) : '***'}
          </p>
          <p className={`text-sm ${totalChangePercent24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {showValues ? formatCurrency(totalChange24h) : '***'}
          </p>
        </div>
        
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-slate-400 text-sm">Total Assets</h3>
            <Settings className="w-4 h-4 text-slate-400" />
          </div>
          <p className="text-2xl font-bold text-white">{assets.length}</p>
          <p className="text-sm text-slate-400">{exchanges.length} exchanges connected</p>
        </div>
      </div>

      {/* Portfolio Charts & Analysis */}
      {assets.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Portfolio Allocation Chart */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
              <PieChart className="w-5 h-5 mr-2" />
              Portfolio Allocation
            </h2>
            {assets.length > 0 ? (
              <div className="h-80">
                <PortfolioChart
                  data={assets.map(asset => ({
                    symbol: asset.symbol,
                    value: asset.value,
                    percentage: (asset.value / totalValue) * 100,
                  }))}
                  className="h-full"
                />
              </div>
            ) : (
              <div className="h-80 flex items-center justify-center text-slate-400">
                <div className="text-center">
                  <PieChart className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Add assets to see allocation</p>
                </div>
              </div>
            )}
          </div>

          {/* Portfolio Performance */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
              <BarChart3 className="w-5 h-5 mr-2" />
              Performance Overview
            </h2>
            <div className="space-y-4">
              {/* Top Performer */}
              <div className="bg-slate-700 rounded-lg p-4">
                <h4 className="text-sm font-medium text-slate-300 mb-2">Best Performer (24h)</h4>
                {assets.length > 0 ? (
                  (() => {
                    const bestAsset = [...assets].sort((a, b) => b.changePercent24h - a.changePercent24h)[0];
                    return (
                      <div className="flex justify-between items-center">
                        <span className="text-white font-medium">{bestAsset.symbol}</span>
                        <span className="text-green-400 flex items-center">
                          <TrendingUp className="w-4 h-4 mr-1" />
                          +{bestAsset.changePercent24h.toFixed(2)}%
                        </span>
                      </div>
                    );
                  })()
                ) : (
                  <p className="text-slate-400">No assets to analyze</p>
                )}
              </div>

              {/* Worst Performer */}
              <div className="bg-slate-700 rounded-lg p-4">
                <h4 className="text-sm font-medium text-slate-300 mb-2">Worst Performer (24h)</h4>
                {assets.length > 0 ? (
                  (() => {
                    const worstAsset = [...assets].sort((a, b) => a.changePercent24h - b.changePercent24h)[0];
                    return (
                      <div className="flex justify-between items-center">
                        <span className="text-white font-medium">{worstAsset.symbol}</span>
                        <span className="text-red-400 flex items-center">
                          <TrendingDown className="w-4 h-4 mr-1" />
                          {worstAsset.changePercent24h.toFixed(2)}%
                        </span>
                      </div>
                    );
                  })()
                ) : (
                  <p className="text-slate-400">No assets to analyze</p>
                )}
              </div>

              {/* Largest Holding */}
              <div className="bg-slate-700 rounded-lg p-4">
                <h4 className="text-sm font-medium text-slate-300 mb-2">Largest Holding</h4>
                {assets.length > 0 ? (
                  (() => {
                    const largestAsset = [...assets].sort((a, b) => b.value - a.value)[0];
                    const percentage = ((largestAsset.value / totalValue) * 100).toFixed(1);
                    return (
                      <div className="flex justify-between items-center">
                        <span className="text-white font-medium">{largestAsset.symbol}</span>
                        <div className="text-right">
                          <span className="text-slate-300">{showValues ? formatCurrency(largestAsset.value) : '***'}</span>
                          <p className="text-xs text-slate-400">{percentage}% of portfolio</p>
                        </div>
                      </div>
                    );
                  })()
                ) : (
                  <p className="text-slate-400">No assets to analyze</p>
                )}
              </div>

              {/* Portfolio Diversity Score */}
              <div className="bg-slate-700 rounded-lg p-4">
                <h4 className="text-sm font-medium text-slate-300 mb-2">Diversity Score</h4>
                {assets.length > 0 ? (
                  (() => {
                    // Calculate Herfindahl-Hirschman Index for portfolio concentration
                    const totalVal = totalValue;
                    const hhi = assets.reduce((sum, asset) => {
                      const weight = asset.value / totalVal;
                      return sum + (weight * weight);
                    }, 0);
                    const diversityScore = Math.round((1 - hhi) * 100);
                    const diversityLabel = diversityScore > 80 ? 'Excellent' : 
                                         diversityScore > 60 ? 'Good' : 
                                         diversityScore > 40 ? 'Moderate' : 'Poor';
                    const diversityColor = diversityScore > 80 ? 'text-green-400' : 
                                          diversityScore > 60 ? 'text-blue-400' : 
                                          diversityScore > 40 ? 'text-yellow-400' : 'text-red-400';
                    
                    return (
                      <div className="flex justify-between items-center">
                        <span className="text-white font-medium">{diversityScore}/100</span>
                        <span className={`${diversityColor} font-medium`}>{diversityLabel}</span>
                      </div>
                    );
                  })()
                ) : (
                  <p className="text-slate-400">Add more assets for better diversity</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Connected Exchanges */}
      {exchanges.length > 0 && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Connected Exchanges</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {exchanges.map((exchange) => (
              <div key={exchange.id} className="bg-slate-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-white">{exchange.name}</h3>
                  <div className={`w-2 h-2 rounded-full ${exchange.isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                </div>
                <p className="text-sm text-slate-400 mb-3">
                  Last sync: {new Date(exchange.lastSync).toLocaleString()}
                </p>
                <button
                  onClick={() => syncExchange(exchange.id)}
                  disabled={isLoading}
                  className="w-full py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded text-sm transition-colors"
                >
                  {isLoading ? 'Syncing...' : 'Sync Now'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Assets Table */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div className="p-6 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-white">Your Assets</h2>
        </div>
        
        {assets.length === 0 ? (
          <div className="p-12 text-center">
            <div className="text-slate-400 mb-4">
              <DollarSign className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg">No assets in your portfolio yet</p>
              <p className="text-sm">Add assets manually or connect an exchange to get started</p>
            </div>
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => setShowAddAsset(true)}
                className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
              >
                Add Asset Manually
              </button>
              <button
                onClick={() => setShowConnectExchange(true)}
                className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
              >
                Connect Exchange
              </button>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Asset</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Holdings</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">24h Change</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Source</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {assets.map((asset) => (
                  <tr key={asset.id} className="hover:bg-slate-700">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-bold mr-3">
                          {asset.symbol.slice(0, 2)}
                        </div>
                        <div>
                          <div className="text-sm font-medium text-white">{asset.symbol}</div>
                          <div className="text-sm text-slate-400">{asset.name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                      {showValues ? asset.amount.toFixed(6) : '***'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                      {formatCurrency(asset.currentPrice)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={asset.changePercent24h >= 0 ? 'text-green-400' : 'text-red-400'}>
                        {formatPercent(asset.changePercent24h)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                      {formatCurrency(asset.value)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        asset.source === 'manual' 
                          ? 'bg-gray-100 text-gray-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {asset.source}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => {/* Edit asset logic */}}
                          className="text-blue-400 hover:text-blue-300"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => removeAsset(asset.id)}
                          className="text-red-400 hover:text-red-300"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Asset Modal */}
      <AddAssetModal 
        isOpen={showAddAsset} 
        onClose={() => setShowAddAsset(false)} 
        onAdd={addAsset}
      />

      {/* Connect Exchange Modal */}
      <ConnectExchangeModal 
        isOpen={showConnectExchange} 
        onClose={() => setShowConnectExchange(false)} 
        onConnect={addExchange}
      />
    </div>
  );
};

// Add Asset Modal Component
const AddAssetModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onAdd: (asset: any) => void;
}> = ({ isOpen, onClose, onAdd }) => {
  const [formData, setFormData] = useState({
    symbol: '',
    name: '',
    amount: '',
    avgBuyPrice: '',
    currentPrice: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const asset = {
      symbol: formData.symbol.toUpperCase(),
      name: formData.name,
      amount: parseFloat(formData.amount),
      avgBuyPrice: parseFloat(formData.avgBuyPrice),
      currentPrice: parseFloat(formData.currentPrice),
      change24h: 0,
      changePercent24h: 0,
      source: 'manual' as const,
    };
    
    onAdd(asset);
    toast.success('Asset added successfully!');
    onClose();
    setFormData({ symbol: '', name: '', amount: '', avgBuyPrice: '', currentPrice: '' });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold text-white mb-4">Add Asset Manually</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Symbol</label>
            <input
              type="text"
              value={formData.symbol}
              onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="BTC"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Bitcoin"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Amount</label>
            <input
              type="number"
              step="any"
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="0.5"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Average Buy Price ($)</label>
            <input
              type="number"
              step="any"
              value={formData.avgBuyPrice}
              onChange={(e) => setFormData({ ...formData, avgBuyPrice: e.target.value })}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="43000"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Current Price ($)</label>
            <input
              type="number"
              step="any"
              value={formData.currentPrice}
              onChange={(e) => setFormData({ ...formData, currentPrice: e.target.value })}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="45000"
              required
            />
          </div>
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 border border-slate-600 text-slate-300 rounded-lg hover:bg-slate-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
            >
              Add Asset
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Connect Exchange Modal Component
const ConnectExchangeModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onConnect: (exchange: any) => void;
}> = ({ isOpen, onClose, onConnect }) => {
  const [selectedExchange, setSelectedExchange] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [secretKey, setSecretKey] = useState('');

  const exchanges = [
    { id: 'binance', name: 'Binance', icon: '🟡' },
    { id: 'coinbase', name: 'Coinbase Pro', icon: '🔵' },
    { id: 'kraken', name: 'Kraken', icon: '🟣' },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const exchangeData = {
      name: exchanges.find(ex => ex.id === selectedExchange)?.name || '',
      apiKey,
      secretKey,
    };
    
    onConnect(exchangeData);
    toast.success('Exchange connection added! Click "Sync Now" to import your assets.');
    onClose();
    setSelectedExchange('');
    setApiKey('');
    setSecretKey('');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold text-white mb-4">Connect Exchange</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Select Exchange</label>
            <div className="space-y-2">
              {exchanges.map((exchange) => (
                <label key={exchange.id} className="flex items-center p-3 bg-slate-700 rounded-lg cursor-pointer hover:bg-slate-600 transition-colors">
                  <input
                    type="radio"
                    name="exchange"
                    value={exchange.id}
                    checked={selectedExchange === exchange.id}
                    onChange={(e) => setSelectedExchange(e.target.value)}
                    className="mr-3"
                    required
                  />
                  <span className="mr-2 text-lg">{exchange.icon}</span>
                  <span className="text-white">{exchange.name}</span>
                </label>
              ))}
            </div>
          </div>
          
          {selectedExchange && (
            <>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">API Key</label>
                <input
                  type="text"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your API key"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Secret Key</label>
                <input
                  type="password"
                  value={secretKey}
                  onChange={(e) => setSecretKey(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your secret key"
                  required
                />
              </div>
              <div className="text-xs text-slate-400 bg-slate-700 p-3 rounded-lg">
                <p className="mb-1">⚠️ <strong>Security Note:</strong></p>
                <p>• Only use read-only API keys</p>
                <p>• Never share your secret keys</p>
                <p>• Keys are stored securely and encrypted</p>
              </div>
            </>
          )}
          
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 border border-slate-600 text-slate-300 rounded-lg hover:bg-slate-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
            >
              Connect
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Portfolio;
