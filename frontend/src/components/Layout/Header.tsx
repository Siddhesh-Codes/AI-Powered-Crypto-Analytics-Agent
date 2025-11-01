import React, { useState, useRef, useEffect } from 'react';
import { Search, Bell, User, LogOut, Settings as SettingsIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useMarketStore } from '../../store/marketStore';
import toast from 'react-hot-toast';

/**
 * Header Component
 * Top navigation bar with search, notifications, and user menu
 */
const Header: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [notifications, setNotifications] = useState([
    { id: 1, title: 'Bitcoin Alert', message: 'BTC reached your target price of $45,000', time: '2 minutes ago', unread: true },
    { id: 2, title: 'Portfolio Update', message: 'Your portfolio is up 5.2% today', time: '1 hour ago', unread: true },
    { id: 3, title: 'Risk Alert', message: 'High volatility detected in your ETH position', time: '3 hours ago', unread: false },
  ]);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const notificationRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLDivElement>(null);
  
  const { user, logout } = useAuth();
  const { topCryptos, searchCryptos } = useMarketStore();
  const navigate = useNavigate();

  const unreadCount = notifications.filter(n => n.unread).length;

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearchResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      try {
        // Search in existing topCryptos first for instant results
        const localResults = topCryptos.filter(crypto => 
          crypto.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
          crypto.name.toLowerCase().includes(searchQuery.toLowerCase())
        );
        
        if (localResults.length > 0) {
          setSearchResults(localResults);
          setShowSearchResults(true);
        } else {
          // If no local results, search using API
          const apiResults = await searchCryptos(searchQuery);
          setSearchResults(apiResults);
          setShowSearchResults(true);
          
          if (apiResults.length === 0) {
            toast.error(`No cryptocurrencies found for "${searchQuery}"`);
          } else {
            toast.success(`Found ${apiResults.length} result(s) for "${searchQuery}"`);
          }
        }
      } catch (error) {
        console.error('Search error:', error);
        toast.error('Search failed. Please try again.');
      }
    }
  };

  // Handle search input change for real-time search
  const handleSearchInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);
    
    if (value.trim()) {
      // Real-time search in local data
      const localResults = topCryptos.filter(crypto => 
        crypto.symbol.toLowerCase().includes(value.toLowerCase()) ||
        crypto.name.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 5); // Limit to 5 results for dropdown
      
      setSearchResults(localResults);
      setShowSearchResults(true);
    } else {
      setShowSearchResults(false);
    }
  };

  // Handle clicking on a search result
  const handleSearchResultClick = (crypto: any) => {
    setSearchQuery('');
    setShowSearchResults(false);
    // Navigate to crypto analysis page or dashboard with selected crypto
    navigate(`/analytics?symbol=${crypto.symbol}`);
    toast.success(`Viewing ${crypto.name} (${crypto.symbol})`);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const markAllAsRead = () => {
    setNotifications(notifications.map(notification => ({
      ...notification,
      unread: false
    })));
  };

  const markNotificationAsRead = (id: number) => {
    setNotifications(notifications.map(notification => 
      notification.id === id ? { ...notification, unread: false } : notification
    ));
  };

  const getUserInitials = (name: string | undefined) => {
    // Try to get initials from name
    if (name && typeof name === 'string' && name.trim() !== '') {
      try {
        return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
      } catch (error) {
        console.error('Error generating initials from name:', error);
      }
    }
    
    // Fallback to email initials
    if (user?.email && typeof user.email === 'string') {
      try {
        return user.email.substring(0, 2).toUpperCase();
      } catch (error) {
        console.error('Error generating initials from email:', error);
      }
    }
    
    // Final fallback
    return 'U';
  };

  return (
    <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
      <div className="flex justify-between items-center">
        {/* Search Bar */}
        <div className="flex-1 max-w-md" ref={searchRef}>
          <form onSubmit={handleSearch} className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search cryptocurrencies..."
              value={searchQuery}
              onChange={handleSearchInput}
              className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            
            {/* Search Results Dropdown */}
            {showSearchResults && searchResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-slate-700 border border-slate-600 rounded-lg shadow-xl z-50 max-h-80 overflow-y-auto">
                {searchResults.map((crypto, index) => (
                  <div
                    key={crypto.symbol || index}
                    onClick={() => handleSearchResultClick(crypto)}
                    className="flex items-center justify-between p-3 hover:bg-slate-600 cursor-pointer border-b border-slate-600 last:border-b-0"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xs">
                        {crypto.symbol.substring(0, 2)}
                      </div>
                      <div>
                        <div className="font-medium text-white">{crypto.name}</div>
                        <div className="text-sm text-slate-400">{crypto.symbol}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-white">${crypto.price?.toLocaleString()}</div>
                      <div className={`text-sm ${crypto.priceChangePercent24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {crypto.priceChangePercent24h >= 0 ? '+' : ''}{crypto.priceChangePercent24h?.toFixed(2)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </form>
        </div>

        {/* Right Side Actions */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <div className="relative" ref={notificationRef}>
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 text-slate-400 hover:text-white transition-colors"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Notifications Dropdown */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50">
                <div className="p-4 border-b border-slate-700">
                  <h3 className="text-white font-semibold">Notifications</h3>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {notifications.map((notification) => (
                    <div 
                      key={notification.id} 
                      onClick={() => markNotificationAsRead(notification.id)}
                      className={`p-4 border-b border-slate-700 hover:bg-slate-700 cursor-pointer transition-colors ${notification.unread ? 'bg-blue-900/20' : ''}`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h4 className="text-white font-medium text-sm">{notification.title}</h4>
                          <p className="text-slate-400 text-xs mt-1">{notification.message}</p>
                        </div>
                        {notification.unread && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full ml-2 mt-1"></div>
                        )}
                      </div>
                      <p className="text-slate-500 text-xs mt-2">{notification.time}</p>
                    </div>
                  ))}
                </div>
                <div className="p-3 border-t border-slate-700">
                  <button 
                    onClick={markAllAsRead}
                    className="text-blue-400 text-sm hover:text-blue-300 transition-colors"
                  >
                    Mark all as read
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* User Profile Menu */}
          <div className="relative" ref={userMenuRef}>
            <button 
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-3 hover:bg-slate-700 rounded-lg p-2 transition-colors"
            >
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <span className="text-sm font-semibold text-white">
                  {getUserInitials(user?.name)}
                </span>
              </div>
              <div className="text-sm text-left">
                <p className="text-white font-medium">{user?.name || user?.username || user?.email || 'User'}</p>
                <p className="text-slate-400">Free Plan</p>
              </div>
            </button>

            {/* User Menu Dropdown */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50">
                <div className="p-3 border-b border-slate-700">
                  <p className="text-white font-medium">{user?.name || user?.username || 'User'}</p>
                  <p className="text-slate-400 text-sm">{user?.email}</p>
                </div>
                <div className="py-2">
                  <button 
                    onClick={() => {
                      navigate('/settings');
                      setShowUserMenu(false);
                    }}
                    className="w-full text-left px-4 py-2 text-slate-300 hover:bg-slate-700 hover:text-white flex items-center space-x-2"
                  >
                    <SettingsIcon className="w-4 h-4" />
                    <span>Settings</span>
                  </button>
                  <button 
                    onClick={() => {
                      navigate('/profile');
                      setShowUserMenu(false);
                    }}
                    className="w-full text-left px-4 py-2 text-slate-300 hover:bg-slate-700 hover:text-white flex items-center space-x-2"
                  >
                    <User className="w-4 h-4" />
                    <span>Profile</span>
                  </button>
                </div>
                <div className="border-t border-slate-700 py-2">
                  <button 
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-red-400 hover:bg-slate-700 hover:text-red-300 flex items-center space-x-2"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
