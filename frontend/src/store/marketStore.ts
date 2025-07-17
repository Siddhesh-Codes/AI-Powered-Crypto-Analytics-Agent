import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { 
  cryptoAPI, 
  MarketData, 
  GlobalMetrics, 
  PriceHistory, 
  TechnicalIndicators, 
  MarketSentiment 
} from '../services/cryptoAPI';
import { enhancedCryptoAPI, EnhancedCryptoData } from '../services/enhancedCryptoAPI';
import toast from 'react-hot-toast';

interface MarketState {
  // Data
  topCryptos: MarketData[];
  globalMetrics: GlobalMetrics | null;
  priceHistory: Record<string, PriceHistory[]>;
  technicalIndicators: Record<string, TechnicalIndicators>;
  marketSentiment: MarketSentiment | null;
  
  // UI State
  isLoading: boolean;
  error: string | null;
  selectedCrypto: string | null;
  timeframe: '1h' | '24h' | '7d' | '30d' | '1y';
  autoRefresh: boolean;
  refreshInterval: NodeJS.Timeout | null;
  
  // Actions
  fetchTopCryptos: (limit?: number) => Promise<void>;
  fetchGlobalMetrics: () => Promise<void>;
  fetchPriceHistory: (symbol: string, timeframe: string) => Promise<void>;
  fetchTechnicalIndicators: (symbol: string) => Promise<void>;
  fetchMarketSentiment: () => Promise<void>;
  searchCryptos: (query: string) => Promise<MarketData[]>;
  getCryptoQuote: (symbol: string) => Promise<MarketData | null>;
  
  // Utility Actions
  setSelectedCrypto: (symbol: string | null) => void;
  setTimeframe: (timeframe: '1h' | '24h' | '7d' | '30d' | '1y') => void;
  setAutoRefresh: (enabled: boolean) => void;
  clearError: () => void;
  refreshAllData: () => Promise<void>;
  startAutoRefresh: () => void;
  stopAutoRefresh: () => void;
}

/**
 * Market Data Store
 * Manages cryptocurrency market data, price history, and analytics
 */
export const useMarketStore = create<MarketState>()(
  subscribeWithSelector((set, get) => ({
    // Initial State
    topCryptos: [],
    globalMetrics: null,
    priceHistory: {},
    technicalIndicators: {},
    marketSentiment: null,
    
    isLoading: false,
    error: null,
    selectedCrypto: null,
    timeframe: '24h',
    autoRefresh: true,
    refreshInterval: null,

    // Fetch top cryptocurrencies with stable daily data
    fetchTopCryptos: async (limit = 100) => {
      try {
        set({ isLoading: true, error: null });
        
        // Use enhanced API for stable market data
        console.log('� Fetching daily crypto data...');
        const enhancedData = await enhancedCryptoAPI.fetchRealTimePrices();
        
        // Convert to MarketData format with null safety
        const marketData: MarketData[] = enhancedData.slice(0, limit).map(crypto => ({
          id: crypto?.id || '',
          symbol: crypto?.symbol || '',
          name: crypto?.name || '',
          price: crypto?.price || 0,
          priceChange24h: crypto?.change24h || 0,
          priceChangePercent24h: crypto?.changePercent24h || 0,
          marketCap: crypto?.marketCap || 0,
          marketCapChange24h: (crypto?.change24h || 0) * ((crypto?.marketCap || 0) / (crypto?.price || 1)), // Approximate
          volume24h: crypto?.volume24h || 0,
          volumeChange24h: 0, // Not provided by enhanced API
          circulatingSupply: (crypto?.marketCap || 0) / (crypto?.price || 1),
          totalSupply: (crypto?.marketCap || 0) / (crypto?.price || 1),
          maxSupply: null,
          rank: crypto?.rank || 0,
          lastUpdated: crypto?.lastUpdated ? new Date(crypto.lastUpdated).toISOString() : new Date().toISOString(),
        }));
        
        set({ topCryptos: marketData, isLoading: false });
        
        // Log success with source info
        console.log(`✅ Fetched ${marketData.length} cryptocurrencies for daily analysis: ${enhancedData[0]?.source || 'Enhanced API'}`);
        
        // Update price history for charts
        const state = get();
        enhancedData.forEach(crypto => {
          if (crypto.priceHistory && crypto.priceHistory.length > 0) {
            const priceHistory: PriceHistory[] = crypto.priceHistory.map((price, index) => ({
              timestamp: Date.now() - (crypto.priceHistory.length - index) * 3600000, // 1 hour intervals
              price: price,
              volume: crypto.volume24h / 24, // Approximate hourly volume
              marketCap: price * (crypto.marketCap / crypto.price)
            }));
            
            state.priceHistory[crypto.symbol] = priceHistory;
          }
        });
        
        set({ priceHistory: { ...state.priceHistory } });
        
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch cryptocurrencies';
        console.error('❌ Market store - fetchTopCryptos error:', error);
        set({ error: errorMessage, isLoading: false });
        
        // Try fallback to original API
        try {
          console.log('🔄 Falling back to original API...');
          const fallbackData = await cryptoAPI.getTopCryptos(limit);
          set({ topCryptos: fallbackData, isLoading: false, error: null });
          console.log('✅ Fallback data loaded successfully');
        } catch (fallbackError) {
          console.error('❌ Fallback also failed:', fallbackError);
        }
      }
    },

    // Fetch global market metrics
    fetchGlobalMetrics: async () => {
      try {
        set({ isLoading: true, error: null });
        const data = await cryptoAPI.getGlobalMetrics();
        set({ globalMetrics: data, isLoading: false });
        
        // Log success
        console.log('Fetched global market metrics');
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch global metrics';
        console.error('Market store - fetchGlobalMetrics error:', error);
        set({ error: errorMessage, isLoading: false });
        // Don't show toast error since API has fallback - data should still be available
      }
    },

    // Fetch price history for a specific crypto
    fetchPriceHistory: async (symbol: string, timeframe: string) => {
      try {
        const data = await cryptoAPI.getPriceHistory(symbol, timeframe);
        set(state => ({
          priceHistory: {
            ...state.priceHistory,
            [symbol]: data
          }
        }));
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch price history';
        toast.error(errorMessage);
      }
    },

    // Fetch technical indicators
    fetchTechnicalIndicators: async (symbol: string) => {
      try {
        const data = await cryptoAPI.getTechnicalIndicators(symbol);
        set(state => ({
          technicalIndicators: {
            ...state.technicalIndicators,
            [symbol]: data
          }
        }));
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch technical indicators';
        toast.error(errorMessage);
      }
    },

    // Fetch market sentiment
    fetchMarketSentiment: async () => {
      try {
        const data = await cryptoAPI.getMarketSentiment();
        set({ marketSentiment: data });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch market sentiment';
        toast.error(errorMessage);
      }
    },

    // Search cryptocurrencies
    searchCryptos: async (query: string) => {
      try {
        return await cryptoAPI.searchCryptos(query);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to search cryptocurrencies';
        toast.error(errorMessage);
        return [];
      }
    },

    // Get single crypto quote
    getCryptoQuote: async (symbol: string) => {
      try {
        return await cryptoAPI.getCryptoQuote(symbol);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch crypto quote';
        toast.error(errorMessage);
        return null;
      }
    },

    // Set selected cryptocurrency
    setSelectedCrypto: (symbol: string | null) => {
      set({ selectedCrypto: symbol });
    },

    // Set timeframe
    setTimeframe: (timeframe: '1h' | '24h' | '7d' | '30d' | '1y') => {
      set({ timeframe });
    },

    // Set auto-refresh
    setAutoRefresh: (enabled: boolean) => {
      set({ autoRefresh: enabled });
      if (enabled) {
        get().startAutoRefresh();
      } else {
        get().stopAutoRefresh();
      }
    },

    // Clear error
    clearError: () => {
      set({ error: null });
    },

    // Refresh all data
    refreshAllData: async () => {
      const { fetchTopCryptos, fetchGlobalMetrics, fetchMarketSentiment } = get();
      await Promise.all([
        fetchTopCryptos(),
        fetchGlobalMetrics(),
        fetchMarketSentiment()
      ]);
    },

    // Start daily updates for stable market overview
    startAutoRefresh: () => {
      const { refreshInterval, autoRefresh } = get();
      if (refreshInterval) clearInterval(refreshInterval);
      
      if (autoRefresh) {
        const interval = setInterval(() => {
          const state = get();
          // Daily refresh for stable market data updates
          console.log('🔄 Daily crypto data update...');
          state.fetchTopCryptos(20);
          state.fetchGlobalMetrics();
          if (state.selectedCrypto) {
            state.fetchTechnicalIndicators(state.selectedCrypto);
            state.fetchPriceHistory(state.selectedCrypto, state.timeframe);
          }
        }, 24 * 60 * 60 * 1000); // 24 hours for daily updates
        
        set({ refreshInterval: interval });
        console.log('✅ Daily auto-refresh started (24-hour intervals)');
      }
    },

    // Stop daily updates
    stopAutoRefresh: () => {
      const { refreshInterval } = get();
      if (refreshInterval) {
        clearInterval(refreshInterval);
        set({ refreshInterval: null });
      }
    },
  }))
);

// Initialize auto-refresh when store loads
useMarketStore.getState().startAutoRefresh();

export default useMarketStore;
