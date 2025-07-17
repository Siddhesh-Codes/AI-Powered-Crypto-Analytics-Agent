import React from 'react';

/**
 * Settings Page Component
 * User preferences, API keys, and application settings
 */
const Settings: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold gradient-text">Settings</h1>
      
      {/* API Configuration */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">API Configuration</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              CoinMarketCap API Key
            </label>
            <input
              type="password"
              className="input-field w-full"
              placeholder="Enter your CMC API key"
            />
            <p className="text-xs text-slate-400 mt-1">
              Get your free API key from CoinMarketCap
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              News API Key
            </label>
            <input
              type="password"
              className="input-field w-full"
              placeholder="Enter your NewsAPI key"
            />
          </div>
        </div>
      </div>

      {/* Notification Settings */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Notifications</h2>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="font-medium">Price Alerts</p>
              <p className="text-sm text-slate-400">Get notified when prices hit your targets</p>
            </div>
            <button className="bg-blue-600 rounded-full w-12 h-6 relative">
              <div className="bg-white rounded-full w-5 h-5 absolute right-0.5 top-0.5"></div>
            </button>
          </div>
          
          <div className="flex justify-between items-center">
            <div>
              <p className="font-medium">Portfolio Updates</p>
              <p className="text-sm text-slate-400">Daily portfolio performance summary</p>
            </div>
            <button className="bg-gray-600 rounded-full w-12 h-6 relative">
              <div className="bg-white rounded-full w-5 h-5 absolute left-0.5 top-0.5"></div>
            </button>
          </div>
          
          <div className="flex justify-between items-center">
            <div>
              <p className="font-medium">Market News</p>
              <p className="text-sm text-slate-400">Important crypto market updates</p>
            </div>
            <button className="bg-blue-600 rounded-full w-12 h-6 relative">
              <div className="bg-white rounded-full w-5 h-5 absolute right-0.5 top-0.5"></div>
            </button>
          </div>
        </div>
      </div>

      {/* Theme Settings */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Appearance</h2>
        <div className="space-y-4">
          <div>
            <p className="font-medium mb-2">Theme</p>
            <div className="grid grid-cols-3 gap-2">
              <button className="p-3 bg-slate-700 rounded-lg border-2 border-blue-500">
                <div className="w-full h-8 bg-slate-800 rounded mb-2"></div>
                <p className="text-xs">Dark</p>
              </button>
              <button className="p-3 bg-slate-700 rounded-lg border-2 border-transparent">
                <div className="w-full h-8 bg-white rounded mb-2"></div>
                <p className="text-xs">Light</p>
              </button>
              <button className="p-3 bg-slate-700 rounded-lg border-2 border-transparent">
                <div className="w-full h-8 bg-gradient-to-r from-slate-800 to-white rounded mb-2"></div>
                <p className="text-xs">Auto</p>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Data & Privacy */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Data & Privacy</h2>
        <div className="space-y-4">
          <button className="btn-secondary w-full">Export Portfolio Data</button>
          <button className="btn-secondary w-full">Delete Account</button>
          <div className="text-xs text-slate-400">
            <p>Your data is stored securely and never shared with third parties.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
