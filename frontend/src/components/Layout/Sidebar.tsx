import React from 'react';
import { NavLink } from 'react-router-dom';

/**
 * Sidebar Navigation Component
 * Provides navigation menu for the application
 */
const Sidebar: React.FC = () => {
  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/analytics', label: 'Analytics', icon: '📈' },
    { path: '/portfolio', label: 'Portfolio', icon: '💼' },
    { path: '/trading-signals', label: 'Trading Signals', icon: '🎯' },
    { path: '/alerts', label: 'Smart Alerts', icon: '🔔' },
    { path: '/news', label: 'News & Sentiment', icon: '📰' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <div className="w-64 bg-slate-800 border-r border-slate-700 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-700">
        <h2 className="text-xl font-bold gradient-text">
          Crypto Analytics
        </h2>
        <p className="text-sm text-slate-400 mt-1">AI-Powered Insights</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 rounded-lg transition-colors duration-200 ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                  }`
                }
              >
                <span className="mr-3 text-lg">{item.icon}</span>
                <span className="font-medium">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-700">
        <div className="text-xs text-slate-500 text-center">
          <p>© 2025 Crypto Analytics</p>
          <p>Final Year Project</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
