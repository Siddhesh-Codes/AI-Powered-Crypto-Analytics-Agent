import { create } from 'zustand';
import toast from 'react-hot-toast';

export interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  url: string;
  published_at: string;
  source: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  relevance_score: number;
}

interface NewsState {
  articles: NewsArticle[];
  isLoading: boolean;
  lastUpdated: string | null;
  
  // Actions
  fetchNews: (limit?: number) => Promise<void>;
  refreshNews: () => Promise<void>;
}

export const useNewsStore = create<NewsState>((set, get) => ({
  articles: [],
  isLoading: false,
  lastUpdated: null,

  fetchNews: async (limit = 20) => {
    set({ isLoading: true });
    
    try {
      const response = await fetch(`http://localhost:8000/api/news?limit=${limit}`);

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          set({
            articles: data.articles,
            lastUpdated: new Date().toISOString(),
            isLoading: false,
          });
          return;
        }
      }
      
      throw new Error('Failed to fetch news');
    } catch (error) {
      console.error('Error fetching news:', error);
      
      // Fallback to mock news
      const mockArticles: NewsArticle[] = [
        {
          id: 'news_1',
          title: 'Bitcoin Reaches New All-Time High Amid Institutional Adoption',
          summary: 'Bitcoin surged to unprecedented levels as major corporations continue to add BTC to their treasury reserves, signaling growing institutional confidence.',
          url: 'https://cryptonews.com/bitcoin-ath-institutional',
          published_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 minutes ago
          source: 'CryptoDB',
          sentiment: 'positive',
          relevance_score: 0.95
        },
        {
          id: 'news_2',
          title: 'Ethereum 2.0 Staking Rewards See Significant Increase',
          summary: 'The latest network upgrade has led to improved staking rewards for ETH holders, with APY reaching new highs this quarter.',
          url: 'https://cryptonews.com/ethereum-staking-rewards',
          published_at: new Date(Date.now() - 1000 * 60 * 90).toISOString(), // 1.5 hours ago
          source: 'CoinDesk',
          sentiment: 'positive',
          relevance_score: 0.88
        },
        {
          id: 'news_3',
          title: 'Regulatory Clarity Brings Stability to Crypto Markets',
          summary: 'New regulatory guidelines from major economies are providing the clarity that institutional investors have been seeking.',
          url: 'https://cryptonews.com/regulatory-clarity',
          published_at: new Date(Date.now() - 1000 * 60 * 180).toISOString(), // 3 hours ago
          source: 'The Block',
          sentiment: 'positive',
          relevance_score: 0.82
        },
        {
          id: 'news_4',
          title: 'DeFi Protocol Launches Revolutionary Yield Farming Solution',
          summary: 'A new decentralized finance protocol has introduced innovative yield farming mechanisms that promise higher returns with lower risk.',
          url: 'https://cryptonews.com/defi-yield-farming',
          published_at: new Date(Date.now() - 1000 * 60 * 240).toISOString(), // 4 hours ago
          source: 'Cointelegraph',
          sentiment: 'positive',
          relevance_score: 0.79
        },
        {
          id: 'news_5', 
          title: 'Market Volatility Concerns Rise Amid Global Economic Uncertainty',
          summary: 'Cryptocurrency markets are showing increased volatility as global economic indicators suggest potential headwinds ahead.',
          url: 'https://cryptonews.com/market-volatility',
          published_at: new Date(Date.now() - 1000 * 60 * 300).toISOString(), // 5 hours ago
          source: 'CryptoNews',
          sentiment: 'negative',
          relevance_score: 0.76
        }
      ];
      
      set({
        articles: mockArticles,
        lastUpdated: new Date().toISOString(),
        isLoading: false,
      });
      
      toast.error('Using mock news data (backend unavailable)');
    }
  },

  refreshNews: async () => {
    const { fetchNews } = get();
    await fetchNews();
    toast.success('News refreshed');
  },
}));
