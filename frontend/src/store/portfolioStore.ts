import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Asset {
  id: string;
  symbol: string;
  name: string;
  amount: number;
  avgBuyPrice: number;
  currentPrice: number;
  value: number;
  change24h: number;
  changePercent24h: number;
  source: 'manual' | 'binance' | 'coinbase' | 'kraken';
}

export interface Exchange {
  id: string;
  name: string;
  apiKey: string;
  secretKey: string;
  isConnected: boolean;
  lastSync: string;
}

interface PortfolioState {
  assets: Asset[];
  exchanges: Exchange[];
  totalValue: number;
  totalChange24h: number;
  totalChangePercent24h: number;
  isLoading: boolean;
  
  // Actions
  addAsset: (asset: Omit<Asset, 'id' | 'value'>) => Promise<void>;
  updateAsset: (id: string, updates: Partial<Asset>) => void;
  removeAsset: (id: string) => void;
  addExchange: (exchange: Omit<Exchange, 'id' | 'isConnected' | 'lastSync'>) => void;
  removeExchange: (id: string) => void;
  syncExchange: (id: string) => Promise<void>;
  calculateTotals: () => void;
  refreshPrices: () => Promise<void>;
}

export const usePortfolioStore = create<PortfolioState>()(
  persist(
    (set, get) => ({
      assets: [],
      exchanges: [],
      totalValue: 0,
      totalChange24h: 0,
      totalChangePercent24h: 0,
      isLoading: false,

      addAsset: async (assetData) => {
        set({ isLoading: true });
        
        try {
          // Try backend API
          const token = localStorage.getItem('token');
          const response = await fetch('http://localhost:8000/api/portfolio/assets', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(assetData),
          });

          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              set((state) => ({
                assets: [...state.assets, data.asset],
                isLoading: false,
              }));
              get().calculateTotals();
              return;
            }
          }
        } catch (error) {
          console.error('Error adding asset via API:', error);
        }

        // Fallback to local storage
        const asset: Asset = {
          ...assetData,
          id: Date.now().toString(),
          value: assetData.amount * assetData.currentPrice,
        };
        
        set((state) => ({
          assets: [...state.assets, asset],
          isLoading: false,
        }));
        
        get().calculateTotals();
      },

      updateAsset: (id, updates) => {
        set((state) => ({
          assets: state.assets.map((asset) =>
            asset.id === id 
              ? { 
                  ...asset, 
                  ...updates, 
                  value: (updates.amount || asset.amount) * (updates.currentPrice || asset.currentPrice)
                }
              : asset
          ),
        }));
        
        get().calculateTotals();
      },

      removeAsset: (id) => {
        set((state) => ({
          assets: state.assets.filter((asset) => asset.id !== id),
        }));
        
        get().calculateTotals();
      },

      addExchange: (exchangeData) => {
        const exchange: Exchange = {
          ...exchangeData,
          id: Date.now().toString(),
          isConnected: false,
          lastSync: new Date().toISOString(),
        };
        
        set((state) => ({
          exchanges: [...state.exchanges, exchange],
        }));
      },

      removeExchange: (id) => {
        set((state) => ({
          exchanges: state.exchanges.filter((exchange) => exchange.id !== id),
        }));
      },

      syncExchange: async (id) => {
        set({ isLoading: true });
        
        try {
          // Simulate API call to exchange
          await new Promise(resolve => setTimeout(resolve, 2000));
          
          // Mock data from exchange
          const mockAssets: Omit<Asset, 'id' | 'value'>[] = [
            {
              symbol: 'BTC',
              name: 'Bitcoin',
              amount: 0.5,
              avgBuyPrice: 43000,
              currentPrice: 45000,
              change24h: 1000,
              changePercent24h: 2.27,
              source: 'binance'
            },
            {
              symbol: 'ETH',
              name: 'Ethereum',
              amount: 2.5,
              avgBuyPrice: 2400,
              currentPrice: 2500,
              change24h: 50,
              changePercent24h: 2.04,
              source: 'binance'
            }
          ];
          
          // Add mock assets
          mockAssets.forEach(asset => {
            get().addAsset(asset);
          });
          
          // Update exchange status
          set((state) => ({
            exchanges: state.exchanges.map((exchange) =>
              exchange.id === id
                ? { ...exchange, isConnected: true, lastSync: new Date().toISOString() }
                : exchange
            ),
          }));
          
        } catch (error) {
          console.error('Failed to sync exchange:', error);
        } finally {
          set({ isLoading: false });
        }
      },

      calculateTotals: () => {
        const { assets } = get();
        
        const totalValue = assets.reduce((sum, asset) => sum + asset.value, 0);
        const totalChange24h = assets.reduce((sum, asset) => sum + (asset.change24h * asset.amount), 0);
        const totalChangePercent24h = totalValue > 0 ? (totalChange24h / (totalValue - totalChange24h)) * 100 : 0;
        
        set({
          totalValue,
          totalChange24h,
          totalChangePercent24h,
        });
      },

      refreshPrices: async () => {
        set({ isLoading: true });
        
        try {
          // Try backend API first
          const token = localStorage.getItem('token');
          const response = await fetch('http://localhost:8000/api/portfolio/refresh-prices', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
          });

          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              // Refresh assets from backend
              const assetsResponse = await fetch('http://localhost:8000/api/portfolio/assets', {
                headers: {
                  'Authorization': `Bearer ${token}`,
                },
              });
              
              if (assetsResponse.ok) {
                const assetsData = await assetsResponse.json();
                if (assetsData.success) {
                  set({
                    assets: assetsData.assets,
                    totalValue: assetsData.summary.totalValue,
                    totalChange24h: assetsData.summary.totalChange24h,
                    totalChangePercent24h: assetsData.summary.totalChangePercent24h,
                    isLoading: false,
                  });
                  return;
                }
              }
            }
          }
          
          // Fallback to mock updates
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          // Mock price updates
          const priceUpdates: Record<string, { price: number; change24h: number; changePercent24h: number }> = {
            'BTC': { price: 45200, change24h: 1200, changePercent24h: 2.73 },
            'ETH': { price: 2520, change24h: 70, changePercent24h: 2.86 },
            'ADA': { price: 0.52, change24h: 0.02, changePercent24h: 4.0 },
            'SOL': { price: 95, change24h: 3, changePercent24h: 3.26 },
          };
          
          set((state) => ({
            assets: state.assets.map((asset) => {
              const update = priceUpdates[asset.symbol];
              if (update) {
                return {
                  ...asset,
                  currentPrice: update.price,
                  change24h: update.change24h,
                  changePercent24h: update.changePercent24h,
                  value: asset.amount * update.price,
                };
              }
              return asset;
            }),
          }));
          
          get().calculateTotals();
          
        } catch (error) {
          console.error('Failed to refresh prices:', error);
        } finally {
          set({ isLoading: false });
        }
      },
    }),
    {
      name: 'portfolio-storage',
    }
  )
);
