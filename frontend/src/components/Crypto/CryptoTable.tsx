import React from 'react';
import { TrendingUp, TrendingDown, Star, ExternalLink } from 'lucide-react';
import { MarketData } from '../../services/cryptoAPI';

/**
 * Crypto Table Component
 * Displays cryptocurrency market data in a table format
 */
interface CryptoTableProps {
  data: MarketData[];
  onCryptoSelect?: (crypto: MarketData) => void;
  watchlist?: string[];
  onToggleWatchlist?: (symbol: string) => void;
  className?: string;
}

export const CryptoTable: React.FC<CryptoTableProps> = ({
  data,
  onCryptoSelect,
  watchlist = [],
  onToggleWatchlist,
  className = '',
}) => {
  const formatCurrency = (value: number | undefined | null) => {
    if (!value || isNaN(value)) {
      return 'N/A';
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: value < 1 ? 6 : 2,
    }).format(value);
  };

  const formatMarketCap = (value: number | undefined | null) => {
    if (!value || isNaN(value)) {
      return 'N/A';
    }
    if (value >= 1e12) {
      return `$${(value / 1e12).toFixed(2)}T`;
    } else if (value >= 1e9) {
      return `$${(value / 1e9).toFixed(2)}B`;
    } else if (value >= 1e6) {
      return `$${(value / 1e6).toFixed(2)}M`;
    } else {
      return `$${value.toLocaleString()}`;
    }
  };

  const formatPercent = (value: number | undefined | null) => {
    if (value === undefined || value === null || isNaN(value)) {
      return 'N/A';
    }
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const isInWatchlist = (symbol: string) => {
    return watchlist.includes(symbol);
  };

  // Safety check for data
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className={`bg-slate-800 border border-slate-700 rounded-xl p-8 text-center ${className}`}>
        <p className="text-slate-400">No cryptocurrency data available</p>
      </div>
    );
  }

  return (
    <div className={`bg-slate-800 border border-slate-700 rounded-xl overflow-hidden ${className}`}>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-900 border-b border-slate-700">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Rank
              </th>
              <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Name
              </th>
              <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">
                Price
              </th>
              <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">
                24h Change
              </th>
              <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">
                Market Cap
              </th>
              <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">
                Volume (24h)
              </th>
              <th className="px-6 py-4 text-center text-xs font-medium text-slate-400 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {data
              .filter(crypto => crypto && crypto.id && crypto.symbol && crypto.name) // Filter out invalid entries
              .map((crypto, index) => (
              <tr 
                key={crypto.id}
                className="hover:bg-slate-700 transition-colors cursor-pointer"
                onClick={() => onCryptoSelect?.(crypto)}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-slate-300">
                    #{crypto.rank}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-8 w-8">
                      <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                        <span className="text-white text-xs font-bold">
                          {crypto.symbol.charAt(0)}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-white">
                        {crypto.name}
                      </div>
                      <div className="text-sm text-slate-400">
                        {crypto.symbol}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <div className="text-sm font-medium text-white">
                    {formatCurrency(crypto.price)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <div className={`flex items-center justify-end text-sm font-medium ${
                    crypto.priceChangePercent24h >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {crypto.priceChangePercent24h >= 0 ? (
                      <TrendingUp className="w-4 h-4 mr-1" />
                    ) : (
                      <TrendingDown className="w-4 h-4 mr-1" />
                    )}
                    {formatPercent(crypto.priceChangePercent24h)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <div className="text-sm font-medium text-white">
                    {formatMarketCap(crypto.marketCap)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <div className="text-sm font-medium text-white">
                    {formatMarketCap(crypto.volume24h)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <div className="flex items-center justify-center space-x-2">
                    {onToggleWatchlist && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onToggleWatchlist(crypto.symbol);
                        }}
                        className={`p-1 rounded hover:bg-slate-600 transition-colors ${
                          isInWatchlist(crypto.symbol) ? 'text-yellow-400' : 'text-slate-400'
                        }`}
                        title={isInWatchlist(crypto.symbol) ? 'Remove from watchlist' : 'Add to watchlist'}
                      >
                        <Star className={`w-4 h-4 ${isInWatchlist(crypto.symbol) ? 'fill-current' : ''}`} />
                      </button>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onCryptoSelect?.(crypto);
                      }}
                      className="p-1 rounded hover:bg-slate-600 transition-colors text-slate-400 hover:text-white"
                      title="View details"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {data.length === 0 && (
        <div className="text-center py-12">
          <div className="text-slate-400 text-lg">No cryptocurrencies found</div>
          <div className="text-slate-500 text-sm mt-2">Try adjusting your search criteria</div>
        </div>
      )}
    </div>
  );
};

/**
 * Compact Crypto List Component
 * Displays a simplified list of cryptocurrencies
 */
interface CompactCryptoListProps {
  data: MarketData[];
  onCryptoSelect?: (crypto: MarketData) => void;
  className?: string;
  showRank?: boolean;
}

export const CompactCryptoList: React.FC<CompactCryptoListProps> = ({
  data = [],
  onCryptoSelect,
  className = '',
  showRank = true,
}) => {
  // Add null safety for data
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className={`flex items-center justify-center p-8 text-gray-500 dark:text-gray-400 ${className}`}>
        No cryptocurrency data available
      </div>
    );
  }

  const formatCurrency = (value: number) => {
    if (!value || isNaN(value)) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: value < 1 ? 6 : 2,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    if (!value || isNaN(value)) return 'N/A';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {data.map((crypto) => (
        <div
          key={crypto.id}
          className="bg-slate-800 border border-slate-700 rounded-lg p-4 hover:bg-slate-700 transition-colors cursor-pointer"
          onClick={() => onCryptoSelect?.(crypto)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {showRank && (
                <div className="text-sm text-slate-400 w-8">
                  #{crypto.rank}
                </div>
              )}
              <div className="flex-shrink-0 h-8 w-8">
                <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                  <span className="text-white text-xs font-bold">
                    {crypto.symbol.charAt(0)}
                  </span>
                </div>
              </div>
              <div>
                <div className="text-sm font-medium text-white">
                  {crypto.name}
                </div>
                <div className="text-xs text-slate-400">
                  {crypto.symbol}
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium text-white">
                {formatCurrency(crypto.price)}
              </div>
              <div className={`text-xs ${
                crypto.priceChangePercent24h >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {formatPercent(crypto.priceChangePercent24h)}
              </div>
            </div>
          </div>
        </div>
      ))}
      
      {data.length === 0 && (
        <div className="text-center py-8">
          <div className="text-slate-400">No cryptocurrencies found</div>
        </div>
      )}
    </div>
  );
};
