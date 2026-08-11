import React, { useState, useEffect } from 'react';

/**
 * Settings Page Component
 * User preferences, API keys, and application settings
 */
const Settings: React.FC = () => {
  // State for notification settings
  const [priceAlerts, setPriceAlerts] = useState(true);
  const [portfolioUpdates, setPortfolioUpdates] = useState(false);
  const [marketNews, setMarketNews] = useState(true);
  
  // State for theme selection - initialize from localStorage
  const [selectedTheme, setSelectedTheme] = useState<'dark' | 'light' | 'auto'>(() => {
    const savedTheme = localStorage.getItem('theme') as 'dark' | 'light' | 'auto';
    return savedTheme || 'dark';
  });

  // Theme change handler (with user interaction feedback)
  const handleThemeChange = (theme: 'dark' | 'light' | 'auto') => {
    setSelectedTheme(theme);
    
    // Apply theme to DOM
    applyThemeToDOM(theme);
    
    // Save to localStorage
    localStorage.setItem('theme', theme);
    
    // Force re-render by dispatching a custom event
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
    
    // Show success message with toast notification
    const themeNames = { dark: 'Dark', light: 'Light', auto: 'Auto' };
    
    // Create a toast notification
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg z-50 transition-all duration-300 transform translate-x-full';
    toast.textContent = `✅ Theme changed to ${themeNames[theme]} mode`;
    toast.style.zIndex = '9999';
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
      toast.style.transform = 'translateX(0)';
    }, 10);
    
    // Remove toast after 3 seconds
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => {
        if (document.body.contains(toast)) {
          document.body.removeChild(toast);
        }
      }, 300);
    }, 3000);
  };

  // Initialize theme on component mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'dark' | 'light' | 'auto';
    if (savedTheme) {
      setSelectedTheme(savedTheme);
      // Apply the saved theme immediately (without toast notification on init)
      applyThemeToDOM(savedTheme);
    } else {
      // Default to dark theme if no preference saved
      setSelectedTheme('dark');
      applyThemeToDOM('dark');
    }
  }, []);

  // Separate function to apply theme to DOM without notifications
  const applyThemeToDOM = (theme: 'dark' | 'light' | 'auto') => {
    const root = document.documentElement;
    const body = document.body;
    
    // Remove all existing theme classes
    root.classList.remove('dark', 'light');
    body.classList.remove('bg-gray-900', 'bg-white', 'text-white', 'text-gray-900');
    
    if (theme === 'light') {
      root.classList.add('light');
      root.setAttribute('data-theme', 'light');
      body.classList.add('bg-white', 'text-gray-900');
    } else if (theme === 'dark') {
      root.classList.add('dark');
      root.setAttribute('data-theme', 'dark');
      body.classList.add('bg-gray-900', 'text-white');
    } else {
      // Auto theme
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const autoTheme = prefersDark ? 'dark' : 'light';
      root.classList.add(autoTheme);
      root.setAttribute('data-theme', autoTheme);
      body.classList.add(prefersDark ? 'bg-gray-900' : 'bg-white', prefersDark ? 'text-white' : 'text-gray-900');
    }
  };

  // Handler functions
  const handleExportPortfolio = () => {
    // Create mock portfolio data
    const portfolioData = {
      exportDate: new Date().toISOString(),
      totalValue: 25000,
      assets: [
        { symbol: 'BTC', amount: 0.5, value: 22500 },
        { symbol: 'ETH', amount: 1.2, value: 2500 }
      ]
    };
    
    // Create and download file
    const dataStr = JSON.stringify(portfolioData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `portfolio-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    alert('Portfolio data exported successfully!');
  };

  const handleDeleteAccount = () => {
    const confirmed = window.confirm(
      'Are you sure you want to delete your account? This action cannot be undone.'
    );
    
    if (confirmed) {
      const doubleConfirm = window.confirm(
        'This will permanently delete all your data, portfolio, and settings. Are you absolutely sure?'
      );
      
      if (doubleConfirm) {
        // In a real app, this would call an API
        alert('Account deletion initiated. You will be logged out shortly.');
        // Here you would typically call logout and redirect
      }
    }
  };

  // Toggle component for better reusability
  const Toggle: React.FC<{ enabled: boolean; onChange: (enabled: boolean) => void }> = ({ enabled, onChange }) => (
    <button
      onClick={() => onChange(!enabled)}
      className={`${
        enabled ? 'bg-blue-600' : 'bg-gray-600'
      } rounded-full w-12 h-6 relative transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800`}
    >
      <div
        className={`bg-white rounded-full w-5 h-5 absolute top-0.5 transition-transform duration-200 ${
          enabled ? 'translate-x-6' : 'translate-x-0.5'
        }`}
      ></div>
    </button>
  );

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold gradient-text">Settings</h1>
      
      {/* Notification Settings */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Notifications</h2>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="font-medium">Price Alerts</p>
              <p className="text-sm text-slate-400">Get notified when prices hit your targets</p>
            </div>
            <Toggle enabled={priceAlerts} onChange={setPriceAlerts} />
          </div>
          
          <div className="flex justify-between items-center">
            <div>
              <p className="font-medium">Portfolio Updates</p>
              <p className="text-sm text-slate-400">Daily portfolio performance summary</p>
            </div>
            <Toggle enabled={portfolioUpdates} onChange={setPortfolioUpdates} />
          </div>
          
          <div className="flex justify-between items-center">
            <div>
              <p className="font-medium">Market News</p>
              <p className="text-sm text-slate-400">Important crypto market updates</p>
            </div>
            <Toggle enabled={marketNews} onChange={setMarketNews} />
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
              <button 
                onClick={() => handleThemeChange('dark')}
                className={`p-3 bg-slate-700 rounded-lg border-2 transition-colors duration-200 hover:bg-slate-600 ${
                  selectedTheme === 'dark' ? 'border-blue-500' : 'border-transparent'
                }`}
              >
                <div className="w-full h-8 bg-slate-800 rounded mb-2"></div>
                <p className="text-xs">Dark</p>
              </button>
              <button 
                onClick={() => handleThemeChange('light')}
                className={`p-3 bg-slate-700 rounded-lg border-2 transition-colors duration-200 hover:bg-slate-600 ${
                  selectedTheme === 'light' ? 'border-blue-500' : 'border-transparent'
                }`}
              >
                <div className="w-full h-8 bg-white rounded mb-2"></div>
                <p className="text-xs">Light</p>
              </button>
              <button 
                onClick={() => handleThemeChange('auto')}
                className={`p-3 bg-slate-700 rounded-lg border-2 transition-colors duration-200 hover:bg-slate-600 ${
                  selectedTheme === 'auto' ? 'border-blue-500' : 'border-transparent'
                }`}
              >
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
          <button 
            onClick={handleExportPortfolio}
            className="btn-secondary w-full hover:bg-slate-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800"
          >
            Export Portfolio Data
          </button>
          <button 
            onClick={handleDeleteAccount}
            className="w-full py-2 px-4 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-gray-800"
          >
            Delete Account
          </button>
          <div className="text-xs text-slate-400">
            <p>Your data is stored securely and never shared with third parties.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
