import React, { useState, useEffect } from 'react';
import { Bell, TrendingUp, TrendingDown, AlertTriangle, Check, X, Plus } from 'lucide-react';
import { useMarketStore } from '../../store/marketStore';
import { usePortfolioStore } from '../../store/portfolioStore';

interface Alert {
  id: string;
  symbol: string;
  type: 'price_above' | 'price_below' | 'change_percent' | 'volume_spike' | 'technical_signal';
  condition: number;
  currentValue: number;
  triggered: boolean;
  createdAt: Date;
  triggeredAt?: Date;
  message: string;
}

/**
 * Real-Time Crypto Alerts System
 * Monitors price movements and technical indicators
 */
const AlertsManager: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [showCreateAlert, setShowCreateAlert] = useState(false);
  const [newAlert, setNewAlert] = useState({
    symbol: 'BTC',
    type: 'price_above' as Alert['type'],
    condition: 0
  });

  const { topCryptos } = useMarketStore();
  const { assets } = usePortfolioStore();

  // Simulate alert checking (in real app, this would be WebSocket based)
  useEffect(() => {
    const checkAlerts = () => {
      setAlerts(prevAlerts => 
        prevAlerts.map(alert => {
          const crypto = topCryptos.find(c => c.symbol === alert.symbol);
          if (!crypto || alert.triggered) return alert;

          let shouldTrigger = false;
          let currentValue = 0;

          switch (alert.type) {
            case 'price_above':
              currentValue = crypto.price;
              shouldTrigger = crypto.price >= alert.condition;
              break;
            case 'price_below':
              currentValue = crypto.price;
              shouldTrigger = crypto.price <= alert.condition;
              break;
            case 'change_percent':
              currentValue = crypto.priceChangePercent24h;
              shouldTrigger = Math.abs(crypto.priceChangePercent24h) >= alert.condition;
              break;
            case 'volume_spike':
              currentValue = crypto.volume24h || 0;
              shouldTrigger = (crypto.volume24h || 0) >= alert.condition;
              break;
          }

          if (shouldTrigger && !alert.triggered) {
            // Send notification
            if ('Notification' in window && Notification.permission === 'granted') {
              new Notification(`${alert.symbol} Alert Triggered!`, {
                body: alert.message,
                icon: '/crypto-icon.png'
              });
            }

            return {
              ...alert,
              triggered: true,
              triggeredAt: new Date(),
              currentValue
            };
          }

          return { ...alert, currentValue };
        })
      );
    };

    const interval = setInterval(checkAlerts, 5000); // Check every 5 seconds
    return () => clearInterval(interval);
  }, [topCryptos]);

  // Request notification permission
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const createAlert = () => {
    const alert: Alert = {
      id: Date.now().toString(),
      symbol: newAlert.symbol,
      type: newAlert.type,
      condition: newAlert.condition,
      currentValue: 0,
      triggered: false,
      createdAt: new Date(),
      message: generateAlertMessage(newAlert.symbol, newAlert.type, newAlert.condition)
    };

    setAlerts(prev => [...prev, alert]);
    setShowCreateAlert(false);
    setNewAlert({ symbol: 'BTC', type: 'price_above', condition: 0 });
  };

  const generateAlertMessage = (symbol: string, type: Alert['type'], condition: number): string => {
    switch (type) {
      case 'price_above': return `${symbol} price reached $${condition.toLocaleString()}`;
      case 'price_below': return `${symbol} price dropped to $${condition.toLocaleString()}`;
      case 'change_percent': return `${symbol} price changed by ${condition}%`;
      case 'volume_spike': return `${symbol} volume spiked to ${(condition / 1e9).toFixed(2)}B`;
      default: return `${symbol} alert triggered`;
    }
  };

  const deleteAlert = (id: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  };

  const getAlertIcon = (type: Alert['type']) => {
    switch (type) {
      case 'price_above': return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'price_below': return <TrendingDown className="w-4 h-4 text-red-400" />;
      case 'change_percent': return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      case 'volume_spike': return <Bell className="w-4 h-4 text-blue-400" />;
      default: return <Bell className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold gradient-text">Smart Alerts</h2>
          <p className="text-slate-400">Real-time crypto monitoring & notifications</p>
        </div>
        <button
          onClick={() => setShowCreateAlert(true)}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Create Alert</span>
        </button>
      </div>

      {/* Active Alerts */}
      <div className="grid gap-4">
        {alerts.length === 0 ? (
          <div className="card text-center py-12">
            <Bell className="w-12 h-12 text-slate-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-300 mb-2">No Active Alerts</h3>
            <p className="text-slate-500">Create your first alert to monitor crypto movements</p>
          </div>
        ) : (
          alerts.map(alert => (
            <div
              key={alert.id}
              className={`card border-l-4 ${
                alert.triggered 
                  ? 'border-green-500 bg-green-900/20' 
                  : 'border-blue-500 bg-slate-800'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getAlertIcon(alert.type)}
                  <div>
                    <div className="font-semibold text-slate-200">
                      {alert.symbol} - {alert.type.replace('_', ' ').toUpperCase()}
                    </div>
                    <div className="text-sm text-slate-400">{alert.message}</div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <div className="text-right">
                    <div className="text-sm text-slate-300">
                      Target: {alert.type.includes('price') ? '$' : ''}{alert.condition.toLocaleString()}
                      {alert.type === 'change_percent' ? '%' : ''}
                    </div>
                    <div className="text-sm text-slate-500">
                      Current: {alert.type.includes('price') ? '$' : ''}{alert.currentValue.toLocaleString()}
                      {alert.type === 'change_percent' ? '%' : ''}
                    </div>
                  </div>
                  
                  {alert.triggered ? (
                    <div className="flex items-center space-x-1 text-green-400">
                      <Check className="w-4 h-4" />
                      <span className="text-sm">Triggered</span>
                    </div>
                  ) : (
                    <button
                      onClick={() => deleteAlert(alert.id)}
                      className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-red-400"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Alert Modal */}
      {showCreateAlert && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 p-6 rounded-lg w-full max-w-md mx-4">
            <h3 className="text-xl font-bold mb-4">Create New Alert</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Cryptocurrency
                </label>
                <select
                  value={newAlert.symbol}
                  onChange={(e) => setNewAlert(prev => ({ ...prev, symbol: e.target.value }))}
                  className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg focus:border-blue-500"
                >
                  {topCryptos.slice(0, 20).map(crypto => (
                    <option key={crypto.symbol} value={crypto.symbol}>
                      {crypto.symbol} - {crypto.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Alert Type
                </label>
                <select
                  value={newAlert.type}
                  onChange={(e) => setNewAlert(prev => ({ ...prev, type: e.target.value as Alert['type'] }))}
                  className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg focus:border-blue-500"
                >
                  <option value="price_above">Price Above</option>
                  <option value="price_below">Price Below</option>
                  <option value="change_percent">24h Change %</option>
                  <option value="volume_spike">Volume Spike</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Condition Value
                </label>
                <input
                  type="number"
                  value={newAlert.condition}
                  onChange={(e) => setNewAlert(prev => ({ ...prev, condition: parseFloat(e.target.value) || 0 }))}
                  placeholder={newAlert.type.includes('price') ? 'Enter price' : 'Enter percentage/volume'}
                  className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg focus:border-blue-500"
                />
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowCreateAlert(false)}
                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={createAlert}
                disabled={!newAlert.condition}
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg transition-colors"
              >
                Create Alert
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertsManager;
