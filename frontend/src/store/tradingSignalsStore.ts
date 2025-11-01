import { create } from 'zustand';
import toast from 'react-hot-toast';

export interface TradingSignal {
  id: string;
  symbol: string;
  type: 'BUY' | 'SELL' | 'HOLD';
  strength: number; // 1-100
  indicators: string[];
  entry_price: number;
  target_price: number;
  stop_loss: number;
  timeframe: string;
  generated_at: string;
  ai_confidence: number;
  reason: string;
}

interface TradingSignalsState {
  signals: TradingSignal[];
  isLoading: boolean;
  lastUpdated: string | null;
  
  // Actions
  fetchSignals: (timeframe?: string, limit?: number) => Promise<void>;
  refreshSignals: () => Promise<void>;
}

export const useTradingSignalsStore = create<TradingSignalsState>((set, get) => ({
  signals: [],
  isLoading: false,
  lastUpdated: null,

  fetchSignals: async (timeframe = '1h', limit = 10) => {
    set({ isLoading: true });
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/trading/signals?timeframe=${timeframe}&limit=${limit}`
      );

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          set({
            signals: data.signals,
            lastUpdated: data.generated_at,
            isLoading: false,
          });
          return;
        }
      }
      
      throw new Error('Failed to fetch trading signals');
    } catch (error) {
      console.error('Error fetching trading signals:', error);
      
      // Fallback to mock signals
      const mockSignals: TradingSignal[] = [
        {
          id: 'signal_1',
          symbol: 'BTC',
          type: 'BUY',
          strength: 85,
          indicators: ['RSI Oversold', 'MACD Bullish', 'Volume Breakout'],
          entry_price: 43250,
          target_price: 46710,
          stop_loss: 41087,
          timeframe,
          generated_at: new Date().toISOString(),
          ai_confidence: 87,
          reason: 'Strong bullish momentum with high volume'
        },
        {
          id: 'signal_2',
          symbol: 'ETH',
          type: 'HOLD',
          strength: 65,
          indicators: ['Consolidation', 'Range Bound'],
          entry_price: 2650,
          target_price: 2862,
          stop_loss: 2517,
          timeframe,
          generated_at: new Date().toISOString(),
          ai_confidence: 72,
          reason: 'Market consolidation, waiting for breakout'
        },
        {
          id: 'signal_3',
          symbol: 'ADA',
          type: 'SELL',
          strength: 78,
          indicators: ['RSI Overbought', 'Support Break', 'Volume Spike'],
          entry_price: 0.48,
          target_price: 0.456,
          stop_loss: 0.494,
          timeframe,
          generated_at: new Date().toISOString(),
          ai_confidence: 81,
          reason: 'Bearish momentum with high selling pressure'
        }
      ];
      
      set({
        signals: mockSignals,
        lastUpdated: new Date().toISOString(),
        isLoading: false,
      });
      
      toast.error('Using mock trading signals (backend unavailable)');
    }
  },

  refreshSignals: async () => {
    const { fetchSignals } = get();
    await fetchSignals();
    toast.success('Trading signals refreshed');
  },
}));
