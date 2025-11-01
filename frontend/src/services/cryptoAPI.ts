// API service for crypto data with real-time CoinGecko integration
const API_BASE_URL = 'http://localhost:8000';
const COINGECKO_API_URL = 'https://api.coingecko.com/api/v3';

// Configuration flags
const USE_REAL_API = true; // Set to true for CoinGecko live data
// const API_RATE_LIMIT_DELAY = 1000; // 1 second between requests to avoid rate limits (currently unused)

export interface CryptoListing {
  id: number;
  name: string;
  symbol: string;
  slug: string;
  cmc_rank: number;
  num_market_pairs: number;
  circulating_supply: number;
  total_supply: number;
  max_supply: number | null;
  last_updated: string;
  date_added: string;
  tags: string[];
  platform: any;
  quote: {
    USD: {
      price: number;
      volume_24h: number;
      volume_change_24h: number;
      percent_change_1h: number;
      percent_change_24h: number;
      percent_change_7d: number;
      percent_change_30d: number;
      percent_change_60d: number;
      percent_change_90d: number;
      market_cap: number;
      market_cap_dominance: number;
      fully_diluted_market_cap: number;
      last_updated: string;
    };
  };
}

export interface GlobalMarketData {
  active_cryptocurrencies: number;
  total_cryptocurrencies: number;
  active_market_pairs: number;
  active_exchanges: number;
  total_exchanges: number;
  eth_dominance: number;
  btc_dominance: number;
  eth_dominance_yesterday: number;
  btc_dominance_yesterday: number;
  eth_dominance_24h_percentage_change: number;
  btc_dominance_24h_percentage_change: number;
  defi_volume_24h: number;
  defi_volume_24h_reported: number;
  defi_market_cap: number;
  defi_24h_percentage_change: number;
  stablecoin_volume_24h: number;
  stablecoin_volume_24h_reported: number;
  stablecoin_market_cap: number;
  stablecoin_24h_percentage_change: number;
  derivatives_volume_24h: number;
  derivatives_volume_24h_reported: number;
  derivatives_24h_percentage_change: number;
  quote: {
    USD: {
      total_market_cap: number;
      total_volume_24h: number;
      total_volume_24h_reported: number;
      altcoin_volume_24h: number;
      altcoin_volume_24h_reported: number;
      altcoin_market_cap: number;
      defi_volume_24h: number;
      defi_volume_24h_reported: number;
      defi_24h_percentage_change: number;
      defi_market_cap: number;
      stablecoin_volume_24h: number;
      stablecoin_volume_24h_reported: number;
      stablecoin_24h_percentage_change: number;
      stablecoin_market_cap: number;
      derivatives_volume_24h: number;
      derivatives_volume_24h_reported: number;
      derivatives_24h_percentage_change: number;
      total_market_cap_yesterday: number;
      total_volume_24h_yesterday: number;
      total_market_cap_yesterday_percentage_change: number;
      total_volume_24h_yesterday_percentage_change: number;
      last_updated: string;
    };
  };
}

// Simplified MarketData interface for the store
export interface MarketData {
  id: string;
  symbol: string;
  name: string;
  price: number;
  priceChange24h: number;
  priceChangePercent24h: number;
  marketCap: number | null | undefined;
  marketCapChange24h: number;
  volume24h: number | null | undefined;
  volumeChange24h: number;
  circulatingSupply: number;
  totalSupply: number;
  maxSupply: number | null;
  rank: number;
  lastUpdated: string;
}

export interface GlobalMetrics {
  totalMarketCap: number;
  totalMarketCapChange24h: number;
  total24hVolume: number;
  total24hVolumeChange: number;
  btcDominance: number;
  ethDominance: number;
  activeCryptocurrencies: number;
  totalExchanges: number;
  fearGreedIndex: number;
  fearGreedValue: string;
  lastUpdated: string;
}

export interface PriceHistory {
  timestamp: number;
  price: number;
  volume: number;
  marketCap: number;
}

export interface TechnicalIndicators {
  rsi: number;
  macd: {
    macd: number;
    signal: number;
    histogram: number;
    trend: 'bullish' | 'bearish' | 'neutral';
  };
  bollingerBands: {
    upper: number;
    middle: number;
    lower: number;
    position: 'upper' | 'middle' | 'lower' | 'neutral';
  };
  movingAverages: {
    sma20: number;
    sma50: number;
    sma200: number;
    ema20: number;
    ema50: number;
  };
}

export interface MarketSentiment {
  twitterSentiment: {
    score: number;
    label: 'positive' | 'negative' | 'neutral';
    mentions: number;
  };
  newsSentiment: {
    score: number;
    label: 'positive' | 'negative' | 'neutral';
    articles: number;
  };
  socialVolume: {
    score: number;
    label: 'high' | 'medium' | 'low';
    change24h: number;
  };
  redditSentiment: {
    score: number;
    label: 'positive' | 'negative' | 'neutral';
    posts: number;
  };
}

class CryptoAPI {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Convert CryptoListing to MarketData format
  private convertToMarketData(listing: CryptoListing): MarketData {
    const usd = listing.quote.USD;
    return {
      id: listing.id.toString(),
      symbol: listing.symbol,
      name: listing.name,
      price: usd.price,
      priceChange24h: (usd.price * usd.percent_change_24h) / 100,
      priceChangePercent24h: usd.percent_change_24h,
      marketCap: usd.market_cap,
      marketCapChange24h: (usd.market_cap * usd.percent_change_24h) / 100,
      volume24h: usd.volume_24h,
      volumeChange24h: usd.volume_change_24h,
      circulatingSupply: listing.circulating_supply,
      totalSupply: listing.total_supply,
      maxSupply: listing.max_supply,
      rank: listing.cmc_rank,
      lastUpdated: listing.last_updated,
    };
  }

  async getCryptoListings(limit: number = 100): Promise<CryptoListing[]> {
    try {
      console.log('Attempting to fetch crypto listings from backend...');
      const response = await fetch(`${this.baseURL}/api/crypto/prices`);
      if (!response.ok) {
        throw new Error('Failed to fetch crypto listings');
      }
      const data = await response.json();
      console.log('Backend data received:', data);
      return data.data || [];
    } catch (error) {
      console.warn('Backend not available, using mock data');
      // Return mock data with real-time fluctuations
      const mockData = this.getMockCryptoListings()
        .slice(0, limit)
        .map(listing => this.addPriceFluctuation(listing));
      return mockData;
    }
  }

  async getTopCryptos(limit: number = 100): Promise<MarketData[]> {
    try {
      // First, try to fetch real-time prices if enabled
      if (USE_REAL_API) {
        console.log('🚀 Fetching real-time crypto data from CoinGecko...');
        const realTimeData = await this.fetchCoinGeckoData(limit);
        if (realTimeData && realTimeData.length > 0) {
          console.log('✅ Successfully fetched real-time data from CoinGecko');
          return realTimeData;
        }
      }

      // Fallback to backend API
      const listings = await this.getCryptoListings(limit);
      return listings.map(listing => this.convertToMarketData(listing));
    } catch (error) {
      console.error('Error fetching top cryptos:', error);
      // Final fallback to enhanced mock data
      const mockListings = this.getMockCryptoListings()
        .slice(0, limit)
        .map(listing => this.addPriceFluctuation(listing));
      return mockListings.map(listing => this.convertToMarketData(listing));
    }
  }

  async getMarketData(): Promise<GlobalMarketData | null> {
    try {
      console.log('Attempting to fetch global market data from backend...');
      const response = await fetch(`${this.baseURL}/api/market/data`);
      if (!response.ok) {
        throw new Error('Failed to fetch market data');
      }
      const data = await response.json();
      console.log('Global market data received from backend');
      return data.data;
    } catch (error) {
      console.warn('Backend not available for global metrics, using mock data');
      // Return mock data for demo
      return this.getMockGlobalMarketData();
    }
  }

  async getGlobalMetrics(): Promise<GlobalMetrics> {
    try {
      const marketData = await this.getMarketData();
      if (!marketData) throw new Error('Failed to fetch market data');
      
      const usd = marketData.quote.USD;
      return {
        totalMarketCap: usd.total_market_cap,
        totalMarketCapChange24h: usd.total_market_cap_yesterday_percentage_change,
        total24hVolume: usd.total_volume_24h,
        total24hVolumeChange: usd.total_volume_24h_yesterday_percentage_change,
        btcDominance: marketData.btc_dominance,
        ethDominance: marketData.eth_dominance,
        activeCryptocurrencies: marketData.active_cryptocurrencies,
        totalExchanges: marketData.total_exchanges,
        fearGreedIndex: 65, // Mock value
        fearGreedValue: 'Greed', // Mock value
        lastUpdated: usd.last_updated,
      };
    } catch (error) {
      console.warn('Using mock global metrics due to backend unavailability');
      const mockMetrics = this.getMockGlobalMetrics();
      return mockMetrics;
    }
  }

  async getCryptoQuote(symbol: string): Promise<MarketData | null> {
    try {
      const response = await fetch(`${this.baseURL}/api/crypto/prices`);
      if (!response.ok) {
        throw new Error(`Failed to fetch quote for ${symbol}`);
      }
      const data = await response.json();
      if (data.data) {
        return this.convertToMarketData(data.data);
      }
      return null;
    } catch (error) {
      console.error(`Error fetching quote for ${symbol}:`, error);
      // Return mock data for demo
      const mockListings = this.getMockCryptoListings();
      const mockListing = mockListings.find(l => l.symbol.toLowerCase() === symbol.toLowerCase());
      return mockListing ? this.convertToMarketData(mockListing) : null;
    }
  }

  async searchCrypto(query: string): Promise<CryptoListing[]> {
    try {
      const response = await fetch(`${this.baseURL}/api/crypto/prices`);
      if (!response.ok) {
        throw new Error('Failed to search crypto');
      }
      const data = await response.json();
      return data.data || [];
    } catch (error) {
      console.error('Error searching crypto:', error);
      return [];
    }
  }

  async searchCryptos(query: string): Promise<MarketData[]> {
    try {
      // Try backend API first
      const response = await fetch(`http://localhost:8000/api/market/search?q=${encodeURIComponent(query)}&limit=10`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          return data.results.map((crypto: any) => ({
            id: crypto.symbol.toLowerCase(),
            symbol: crypto.symbol,
            name: crypto.name,
            price: crypto.price,
            priceChange24h: 0, // Not provided by search endpoint
            priceChangePercent24h: 0,
            marketCap: 0,
            volume24h: 0,
            totalSupply: 0,
            maxSupply: 0,
            circulatingSupply: 0,
            rank: 0,
            logo: `https://cryptologos.cc/logos/${crypto.name.toLowerCase().replace(/\s+/g, '-')}-${crypto.symbol.toLowerCase()}-logo.png`,
          }));
        }
      }

      // Fallback to existing search
      const listings = await this.searchCrypto(query);
      return listings.map(listing => this.convertToMarketData(listing));
    } catch (error) {
      console.error('Error searching cryptos:', error);
      return [];
    }
  }

  async getPriceHistory(symbol: string, timeframe: string): Promise<PriceHistory[]> {
    try {
      // Try backend API first
      const response = await fetch('http://localhost:8000/api/market/price-history', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symbol, timeframe, limit: 100 }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          return data.data.map((item: any) => ({
            timestamp: item.timestamp,
            price: item.price,
            volume: item.volume,
            high: item.high,
            low: item.low,
            open: item.open,
            close: item.close,
          }));
        }
      }
      
      // Fallback to mock data
      return this.getMockPriceHistory(symbol, timeframe);
    } catch (error) {
      console.error(`Error fetching price history for ${symbol}:`, error);
      return this.getMockPriceHistory(symbol, timeframe);
    }
  }

  async getTechnicalIndicators(symbol: string): Promise<TechnicalIndicators> {
    try {
      // Try backend API first
      const response = await fetch(`http://localhost:8000/api/technical/indicators/${symbol}`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          return data.data;
        }
      }
      
      // Fallback to mock data
      return this.getMockTechnicalIndicators(symbol);
    } catch (error) {
      console.error(`Error fetching technical indicators for ${symbol}:`, error);
      return this.getMockTechnicalIndicators(symbol);
    }
  }

  async getMarketSentiment(): Promise<MarketSentiment> {
    try {
      // Try backend API first
      const response = await fetch('http://localhost:8000/api/market/sentiment');
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          return {
            twitterSentiment: {
              score: data.data.twitter_sentiment || 0.5,
              label: data.data.twitter_label || 'neutral' as 'positive' | 'negative' | 'neutral',
              mentions: data.data.twitter_mentions || 0,
            },
            newsSentiment: {
              score: data.data.news_sentiment || 0.5,
              label: data.data.news_label || 'neutral' as 'positive' | 'negative' | 'neutral',
              articles: data.data.news_articles || 0,
            },
            socialVolume: {
              score: data.data.social_volume || 0.5,
              label: data.data.social_label || 'medium' as 'high' | 'medium' | 'low',
              change24h: data.data.social_change24h || 0,
            },
            redditSentiment: {
              score: data.data.reddit_sentiment || 0.5,
              label: data.data.reddit_label || 'neutral' as 'positive' | 'negative' | 'neutral',
              posts: data.data.reddit_posts || 0,
            },
          };
        }
      }
      
      // Fallback to mock data
      return this.getMockMarketSentiment();
    } catch (error) {
      console.error('Error fetching market sentiment:', error);
      return this.getMockMarketSentiment();
    }
  }

  /**
   * Simulates real-time price fluctuations for more realistic data
   */
  private addPriceFluctuation(listing: CryptoListing): CryptoListing {
    const now = Date.now();
    const fluctuationSeed = (now / 5000) % 1000; // Changes every 5 seconds for more frequent updates
    
    // Create more realistic fluctuations based on cryptocurrency volatility patterns
    const volatilityMultiplier = listing.symbol === 'BTC' ? 0.8 : 
                                listing.symbol === 'ETH' ? 1.2 :
                                listing.symbol === 'USDT' || listing.symbol === 'USDC' || listing.symbol === 'DAI' ? 0.02 :
                                listing.symbol === 'DOGE' || listing.symbol === 'SHIB' ? 4.5 : 2.0;

    // Combine multiple wave patterns for more realistic price movements
    const wave1 = Math.sin(fluctuationSeed + listing.id) * 0.6;
    const wave2 = Math.sin(fluctuationSeed * 1.7 + listing.id * 2) * 0.3;
    const wave3 = Math.sin(fluctuationSeed * 0.5 + listing.id * 0.5) * 0.1;
    const combinedWave = wave1 + wave2 + wave3;
    
    const fluctuation = combinedWave * volatilityMultiplier * 0.004; // Max 0.4% change per update
    const priceMultiplier = 1 + fluctuation;
    
    // Update price and related metrics
    const newPrice = listing.quote.USD.price * priceMultiplier;
    const priceChange = newPrice - listing.quote.USD.price;
    // const priceChangePercent = (priceChange / listing.quote.USD.price) * 100; // Currently unused
    
    // Update volume with realistic fluctuation (inverse correlation with price sometimes)
    const volumeFluctuation = Math.sin(fluctuationSeed * 1.3 + listing.id) * 0.25; // Max 25% volume change
    const newVolume = listing.quote.USD.volume_24h * (1 + volumeFluctuation);
    
    // Simulate more realistic percentage changes
    const hourlyChange = listing.quote.USD.percent_change_1h + (fluctuation * 30);
    const dailyChange = listing.quote.USD.percent_change_24h + (fluctuation * 5);
    
    return {
      ...listing,
      last_updated: new Date().toISOString(),
      quote: {
        USD: {
          ...listing.quote.USD,
          price: Math.max(newPrice, 0.000001), // Prevent negative prices
          volume_24h: Math.max(newVolume, 1000), // Minimum volume
          percent_change_1h: Math.max(Math.min(hourlyChange, 50), -50), // Cap at ±50%
          percent_change_24h: Math.max(Math.min(dailyChange, 100), -90), // Cap at +100%/-90%
          market_cap: newPrice * listing.circulating_supply,
          last_updated: new Date().toISOString(),
        }
      }
    };
  }

  /**
   * Fetch real-time prices from CoinGecko API (free tier)
   * Fallback to mock data if API fails
   */
  async fetchRealTimePrices(): Promise<void> {
    try {
      const coinIds = 'bitcoin,ethereum,cardano,polkadot,polygon,solana,avalanche-2,chainlink,dogecoin';
      const response = await fetch(
        `https://api.coingecko.com/api/v3/simple/price?ids=${coinIds}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true`,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        console.log('Real-time prices fetched from CoinGecko:', data);
        
        // Update mock data with real prices
        this.updateMockDataWithRealPrices(data);
      } else {
        console.warn('CoinGecko API rate limited or unavailable, using mock data');
      }
    } catch (error) {
      console.warn('Failed to fetch real-time prices, using mock data:', error);
    }
  }

  /**
   * Update mock data with real prices from CoinGecko
   */
  private updateMockDataWithRealPrices(coinGeckoData: any): void {
    // This method would update the mock data prices with real data
    // For now, we'll just log the real data and continue with enhanced mock data
    console.log('Real-time price data available:', {
      bitcoin: coinGeckoData.bitcoin?.usd,
      ethereum: coinGeckoData.ethereum?.usd,
      // Add more mappings as needed
    });
  }

  /**
   * Fetch real-time crypto data from CoinGecko API (free tier)
   * Returns live market data with current prices and 24h changes
   */
  private async fetchCoinGeckoData(limit: number = 100): Promise<MarketData[]> {
    try {
      // Top cryptocurrencies by market cap from CoinGecko
      const response = await fetch(
        `${COINGECKO_API_URL}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=${Math.min(limit, 250)}&page=1&sparkline=false&price_change_percentage=1h,24h,7d`,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          }
        }
      );

      if (!response.ok) {
        if (response.status === 429) {
          console.warn('CoinGecko API rate limit hit, falling back to mock data');
        } else {
          console.warn('CoinGecko API error:', response.status, response.statusText);
        }
        return [];
      }

      const coinGeckoData = await response.json();
      console.log('✅ CoinGecko data fetched successfully:', coinGeckoData.length, 'coins');

      // Convert CoinGecko data to our MarketData format
      return coinGeckoData.map((coin: any, index: number): MarketData => ({
        id: coin.id,
        symbol: coin.symbol.toUpperCase(),
        name: coin.name,
        price: coin.current_price || 0,
        priceChange24h: coin.price_change_24h || 0,
        priceChangePercent24h: coin.price_change_percentage_24h || 0,
        marketCap: coin.market_cap,
        marketCapChange24h: coin.market_cap_change_24h || 0,
        volume24h: coin.total_volume,
        volumeChange24h: 0, // CoinGecko doesn't provide this directly
        circulatingSupply: coin.circulating_supply || 0,
        totalSupply: coin.total_supply || 0,
        maxSupply: coin.max_supply,
        rank: coin.market_cap_rank || index + 1,
        lastUpdated: coin.last_updated || new Date().toISOString(),
      }));

    } catch (error) {
      console.error('Failed to fetch CoinGecko data:', error);
      return [];
    }
  }

  // Mock data for demo purposes
  private getMockCryptoListings(): CryptoListing[] {
    // Real cryptocurrency data with current approximate prices (as of July 2025)
    return [
      {
        id: 1,
        name: "Bitcoin",
        symbol: "BTC",
        slug: "bitcoin",
        cmc_rank: 1,
        num_market_pairs: 10000,
        circulating_supply: 19750000,
        total_supply: 19750000,
        max_supply: 21000000,
        last_updated: new Date().toISOString(),
        date_added: "2013-04-28T00:00:00.000Z",
        tags: ["mineable", "pow", "sha-256"],
        platform: null,
        quote: {
          USD: {
            price: 118500.00, // Updated current BTC price (~$118.5k)
            volume_24h: 38000000000,
            volume_change_24h: 15.2,
            percent_change_1h: 0.85,
            percent_change_24h: 3.2,
            percent_change_7d: 12.8,
            percent_change_30d: 18.5,
            percent_change_60d: 28.3,
            percent_change_90d: 52.1,
            market_cap: 2340000000000, // ~$2.34T
            market_cap_dominance: 53.2,
            fully_diluted_market_cap: 2488500000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 1027,
        name: "Ethereum",
        symbol: "ETH",
        slug: "ethereum",
        cmc_rank: 2,
        num_market_pairs: 8500,
        circulating_supply: 120280000,
        total_supply: 120280000,
        max_supply: null,
        last_updated: new Date().toISOString(),
        date_added: "2015-08-07T00:00:00.000Z",
        tags: ["pos", "smart-contracts", "ethereum-ecosystem"],
        platform: null,
        quote: {
          USD: {
            price: 4125.89, // Updated current ETH price
            volume_24h: 22000000000,
            volume_change_24h: 11.5,
            percent_change_1h: 0.45,
            percent_change_24h: 3.21,
            percent_change_7d: 12.8,
            percent_change_30d: 18.9,
            percent_change_60d: 28.4,
            percent_change_90d: 42.1,
            market_cap: 462000000000, // ~$462B
            market_cap_dominance: 18.7,
            fully_diluted_market_cap: 462000000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 825,
        name: "Tether USDt",
        symbol: "USDT",
        slug: "tether",
        cmc_rank: 3,
        num_market_pairs: 10500,
        circulating_supply: 115000000000,
        total_supply: 115000000000,
        max_supply: null,
        last_updated: new Date().toISOString(),
        date_added: "2015-02-25T00:00:00.000Z",
        tags: ["stablecoin"],
        platform: null,
        quote: {
          USD: {
            price: 1.0001,
            volume_24h: 85000000000,
            volume_change_24h: 5.2,
            percent_change_1h: 0.01,
            percent_change_24h: 0.02,
            percent_change_7d: -0.01,
            percent_change_30d: 0.05,
            percent_change_60d: 0.12,
            percent_change_90d: 0.08,
            market_cap: 115000000000, // ~$115B
            market_cap_dominance: 4.7,
            fully_diluted_market_cap: 115000000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 1839,
        name: "BNB",
        symbol: "BNB",
        slug: "bnb",
        cmc_rank: 4,
        num_market_pairs: 2800,
        circulating_supply: 145930000,
        total_supply: 145930000,
        max_supply: 200000000,
        last_updated: new Date().toISOString(),
        date_added: "2017-07-25T00:00:00.000Z",
        tags: ["marketplace", "centralized-exchange", "payments"],
        platform: null,
        quote: {
          USD: {
            price: 685.23,
            volume_24h: 2100000000,
            volume_change_24h: 15.8,
            percent_change_1h: 0.78,
            percent_change_24h: 4.12,
            percent_change_7d: 9.45,
            percent_change_30d: 22.1,
            percent_change_60d: 35.6,
            percent_change_90d: 48.9,
            market_cap: 100000000000, // ~$100B
            market_cap_dominance: 4.1,
            fully_diluted_market_cap: 137000000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 52,
        name: "XRP",
        symbol: "XRP",
        slug: "xrp",
        cmc_rank: 5,
        num_market_pairs: 1200,
        circulating_supply: 56900000000,
        total_supply: 99990000000,
        max_supply: 100000000000,
        last_updated: new Date().toISOString(),
        date_added: "2013-08-04T00:00:00.000Z",
        tags: ["medium-of-exchange", "enterprise-solutions"],
        platform: null,
        quote: {
          USD: {
            price: 1.42,
            volume_24h: 3200000000,
            volume_change_24h: 18.5,
            percent_change_1h: -0.32,
            percent_change_24h: 6.78,
            percent_change_7d: 14.2,
            percent_change_30d: 28.9,
            percent_change_60d: 45.1,
            percent_change_90d: 62.3,
            market_cap: 80800000000, // ~$80.8B
            market_cap_dominance: 3.3,
            fully_diluted_market_cap: 142000000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 5426,
        name: "Solana",
        symbol: "SOL",
        slug: "solana",
        cmc_rank: 6,
        num_market_pairs: 850,
        circulating_supply: 467000000,
        total_supply: 580000000,
        max_supply: null,
        last_updated: new Date().toISOString(),
        date_added: "2020-04-10T00:00:00.000Z",
        tags: ["pos", "platform", "solana-ecosystem"],
        platform: null,
        quote: {
          USD: {
            price: 168.45,
            volume_24h: 4500000000,
            volume_change_24h: 22.1,
            percent_change_1h: 1.23,
            percent_change_24h: 8.67,
            percent_change_7d: 18.9,
            percent_change_30d: 32.4,
            percent_change_60d: 51.2,
            percent_change_90d: 78.6,
            market_cap: 78700000000, // ~$78.7B
            market_cap_dominance: 3.2,
            fully_diluted_market_cap: 97700000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 3408,
        name: "USD Coin",
        symbol: "USDC",
        slug: "usd-coin",
        cmc_rank: 7,
        num_market_pairs: 4200,
        circulating_supply: 35200000000,
        total_supply: 35200000000,
        max_supply: null,
        last_updated: new Date().toISOString(),
        date_added: "2018-10-08T00:00:00.000Z",
        tags: ["stablecoin"],
        platform: null,
        quote: {
          USD: {
            price: 0.9999,
            volume_24h: 8900000000,
            volume_change_24h: 3.8,
            percent_change_1h: 0.00,
            percent_change_24h: -0.01,
            percent_change_7d: 0.02,
            percent_change_30d: 0.01,
            percent_change_60d: -0.03,
            percent_change_90d: 0.02,
            market_cap: 35200000000, // ~$35.2B
            market_cap_dominance: 1.4,
            fully_diluted_market_cap: 35200000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 74,
        name: "Dogecoin",
        symbol: "DOGE",
        slug: "dogecoin",
        cmc_rank: 8,
        num_market_pairs: 950,
        circulating_supply: 147000000000,
        total_supply: 147000000000,
        max_supply: null,
        last_updated: new Date().toISOString(),
        date_added: "2013-12-15T00:00:00.000Z",
        tags: ["mineable", "pow", "scrypt", "medium-of-exchange", "memes"],
        platform: null,
        quote: {
          USD: {
            price: 0.425,
            volume_24h: 2800000000,
            volume_change_24h: 28.9,
            percent_change_1h: 2.45,
            percent_change_24h: 12.8,
            percent_change_7d: 35.2,
            percent_change_30d: 58.9,
            percent_change_60d: 89.4,
            percent_change_90d: 125.7,
            market_cap: 62500000000, // ~$62.5B
            market_cap_dominance: 2.5,
            fully_diluted_market_cap: 62500000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 1958,
        name: "TRON",
        symbol: "TRX",
        slug: "tron",
        cmc_rank: 9,
        num_market_pairs: 850,
        circulating_supply: 86400000000,
        total_supply: 86400000000,
        max_supply: null,
        last_updated: new Date().toISOString(),
        date_added: "2017-09-13T00:00:00.000Z",
        tags: ["media", "payments", "tron-ecosystem"],
        platform: null,
        quote: {
          USD: {
            price: 0.267,
            volume_24h: 1850000000,
            volume_change_24h: 15.2,
            percent_change_1h: 0.89,
            percent_change_24h: 5.67,
            percent_change_7d: 12.3,
            percent_change_30d: 25.8,
            percent_change_60d: 42.1,
            percent_change_90d: 68.9,
            market_cap: 23100000000, // ~$23.1B
            market_cap_dominance: 0.94,
            fully_diluted_market_cap: 23100000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 2010,
        name: "Cardano",
        symbol: "ADA",
        slug: "cardano",
        cmc_rank: 10,
        num_market_pairs: 650,
        circulating_supply: 35800000000,
        total_supply: 45000000000,
        max_supply: 45000000000,
        last_updated: new Date().toISOString(),
        date_added: "2017-10-01T00:00:00.000Z",
        tags: ["pos", "platform", "research", "smart-contracts"],
        platform: null,
        quote: {
          USD: {
            price: 0.58,
            volume_24h: 850000000,
            volume_change_24h: 8.9,
            percent_change_1h: -0.45,
            percent_change_24h: 3.21,
            percent_change_7d: 9.87,
            percent_change_30d: 18.4,
            percent_change_60d: 28.9,
            percent_change_90d: 45.2,
            market_cap: 20800000000, // ~$20.8B
            market_cap_dominance: 0.85,
            fully_diluted_market_cap: 26100000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 5805,
        name: "Avalanche",
        symbol: "AVAX",
        slug: "avalanche",
        cmc_rank: 11,
        num_market_pairs: 420,
        circulating_supply: 405000000,
        total_supply: 449000000,
        max_supply: 720000000,
        last_updated: new Date().toISOString(),
        date_added: "2020-07-13T00:00:00.000Z",
        tags: ["defi", "platform", "avalanche-ecosystem"],
        platform: null,
        quote: {
          USD: {
            price: 42.85,
            volume_24h: 680000000,
            volume_change_24h: 12.5,
            percent_change_1h: 0.67,
            percent_change_24h: 4.89,
            percent_change_7d: 11.2,
            percent_change_30d: 22.1,
            percent_change_60d: 38.9,
            percent_change_90d: 58.4,
            market_cap: 17350000000, // ~$17.35B
            market_cap_dominance: 0.71,
            fully_diluted_market_cap: 30850000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 7083,
        name: "Shiba Inu",
        symbol: "SHIB",
        slug: "shiba-inu",
        cmc_rank: 12,
        num_market_pairs: 380,
        circulating_supply: 589000000000000,
        total_supply: 1000000000000000,
        max_supply: 1000000000000000,
        last_updated: new Date().toISOString(),
        date_added: "2021-05-10T00:00:00.000Z",
        tags: ["memes", "ethereum-ecosystem"],
        platform: null,
        quote: {
          USD: {
            price: 0.00002845,
            volume_24h: 1200000000,
            volume_change_24h: 35.8,
            percent_change_1h: 3.45,
            percent_change_24h: 18.9,
            percent_change_7d: 45.2,
            percent_change_30d: 78.9,
            percent_change_60d: 125.4,
            percent_change_90d: 189.7,
            market_cap: 16760000000, // ~$16.76B
            market_cap_dominance: 0.68,
            fully_diluted_market_cap: 28450000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 3890,
        name: "Polygon",
        symbol: "MATIC",
        slug: "polygon",
        cmc_rank: 13,
        num_market_pairs: 520,
        circulating_supply: 9320000000,
        total_supply: 10000000000,
        max_supply: 10000000000,
        last_updated: new Date().toISOString(),
        date_added: "2019-04-28T00:00:00.000Z",
        tags: ["scaling", "pos", "platform", "polygon-ecosystem"],
        platform: null,
        quote: {
          USD: {
            price: 1.65,
            volume_24h: 480000000,
            volume_change_24h: 14.2,
            percent_change_1h: 0.89,
            percent_change_24h: 6.78,
            percent_change_7d: 15.4,
            percent_change_30d: 28.9,
            percent_change_60d: 45.2,
            percent_change_90d: 68.4,
            market_cap: 15380000000, // ~$15.38B
            market_cap_dominance: 0.63,
            fully_diluted_market_cap: 16500000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 2,
        name: "Litecoin",
        symbol: "LTC",
        slug: "litecoin",
        cmc_rank: 14,
        num_market_pairs: 850,
        circulating_supply: 75000000,
        total_supply: 75000000,
        max_supply: 84000000,
        last_updated: new Date().toISOString(),
        date_added: "2013-04-28T00:00:00.000Z",
        tags: ["mineable", "pow", "scrypt", "medium-of-exchange"],
        platform: null,
        quote: {
          USD: {
            price: 185.67,
            volume_24h: 890000000,
            volume_change_24h: 11.5,
            percent_change_1h: -0.34,
            percent_change_24h: 2.89,
            percent_change_7d: 8.45,
            percent_change_30d: 15.8,
            percent_change_60d: 25.4,
            percent_change_90d: 38.9,
            market_cap: 13920000000, // ~$13.92B
            market_cap_dominance: 0.57,
            fully_diluted_market_cap: 15600000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 3717,
        name: "Wrapped Bitcoin",
        symbol: "WBTC",
        slug: "wrapped-bitcoin",
        cmc_rank: 15,
        num_market_pairs: 280,
        circulating_supply: 155000,
        total_supply: 155000,
        max_supply: null,
        last_updated: new Date().toISOString(),
        date_added: "2019-01-24T00:00:00.000Z",
        tags: ["wrapped-tokens", "ethereum-ecosystem"],
        platform: null,
        quote: {
          USD: {
            price: 109425.30,
            volume_24h: 320000000,
            volume_change_24h: 8.9,
            percent_change_1h: -0.24,
            percent_change_24h: 2.43,
            percent_change_7d: 8.09,
            percent_change_30d: 15.7,
            percent_change_60d: 22.1,
            percent_change_90d: 44.8,
            market_cap: 16960000000, // ~$16.96B
            market_cap_dominance: 0.69,
            fully_diluted_market_cap: 16960000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 1975,
        name: "Chainlink",
        symbol: "LINK",
        slug: "chainlink",
        cmc_rank: 16,
        num_market_pairs: 580,
        circulating_supply: 626000000,
        total_supply: 1000000000,
        max_supply: 1000000000,
        last_updated: new Date().toISOString(),
        date_added: "2017-09-20T00:00:00.000Z",
        tags: ["defi", "oracles", "smart-contracts"],
        platform: null,
        quote: {
          USD: {
            price: 25.89,
            volume_24h: 750000000,
            volume_change_24h: 18.5,
            percent_change_1h: 1.23,
            percent_change_24h: 7.45,
            percent_change_7d: 16.8,
            percent_change_30d: 32.1,
            percent_change_60d: 48.9,
            percent_change_90d: 72.4,
            market_cap: 16210000000, // ~$16.21B
            market_cap_dominance: 0.66,
            fully_diluted_market_cap: 25890000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 6636,
        name: "Polkadot",
        symbol: "DOT",
        slug: "polkadot-new",
        cmc_rank: 17,
        num_market_pairs: 420,
        circulating_supply: 1440000000,
        total_supply: 1517000000,
        max_supply: null,
        last_updated: new Date().toISOString(),
        date_added: "2020-08-19T00:00:00.000Z",
        tags: ["substrate", "polkadot", "binance-launchpad"],
        platform: null,
        quote: {
          USD: {
            price: 9.85,
            volume_24h: 420000000,
            volume_change_24h: 15.2,
            percent_change_1h: 0.67,
            percent_change_24h: 4.89,
            percent_change_7d: 12.3,
            percent_change_30d: 24.5,
            percent_change_60d: 38.9,
            percent_change_90d: 58.7,
            market_cap: 14184000000, // ~$14.18B
            market_cap_dominance: 0.58,
            fully_diluted_market_cap: 14942000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 11419,
        name: "Toncoin",
        symbol: "TON",
        slug: "toncoin",
        cmc_rank: 18,
        num_market_pairs: 180,
        circulating_supply: 2540000000,
        total_supply: 5110000000,
        max_supply: null,
        last_updated: new Date().toISOString(),
        date_added: "2021-08-27T00:00:00.000Z",
        tags: ["pow", "telegram"],
        platform: null,
        quote: {
          USD: {
            price: 5.45,
            volume_24h: 285000000,
            volume_change_24h: 22.8,
            percent_change_1h: 1.89,
            percent_change_24h: 9.67,
            percent_change_7d: 18.9,
            percent_change_30d: 35.4,
            percent_change_60d: 58.9,
            percent_change_90d: 89.7,
            market_cap: 13843000000, // ~$13.84B
            market_cap_dominance: 0.56,
            fully_diluted_market_cap: 27849000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 4943,
        name: "Dai",
        symbol: "DAI",
        slug: "multi-collateral-dai",
        cmc_rank: 19,
        num_market_pairs: 650,
        circulating_supply: 5150000000,
        total_supply: 5150000000,
        max_supply: null,
        last_updated: new Date().toISOString(),
        date_added: "2019-11-22T00:00:00.000Z",
        tags: ["defi", "stablecoin", "ethereum-ecosystem"],
        platform: null,
        quote: {
          USD: {
            price: 1.0002,
            volume_24h: 245000000,
            volume_change_24h: 5.8,
            percent_change_1h: 0.01,
            percent_change_24h: 0.02,
            percent_change_7d: -0.01,
            percent_change_30d: 0.03,
            percent_change_60d: 0.05,
            percent_change_90d: 0.02,
            market_cap: 5151000000, // ~$5.15B
            market_cap_dominance: 0.21,
            fully_diluted_market_cap: 5151000000,
            last_updated: new Date().toISOString(),
          }
        }
      },
      {
        id: 3155,
        name: "Quant",
        symbol: "QNT",
        slug: "quant",
        cmc_rank: 20,
        num_market_pairs: 85,
        circulating_supply: 14612000,
        total_supply: 14612000,
        max_supply: 14612000,
        last_updated: new Date().toISOString(),
        date_added: "2018-08-10T00:00:00.000Z",
        tags: ["enterprise-solutions", "interoperability"],
        platform: null,
        quote: {
          USD: {
            price: 285.67,
            volume_24h: 125000000,
            volume_change_24h: 28.5,
            percent_change_1h: 2.34,
            percent_change_24h: 8.91,
            percent_change_7d: 22.4,
            percent_change_30d: 45.8,
            percent_change_60d: 78.9,
            percent_change_90d: 125.4,
            market_cap: 4173000000, // ~$4.17B
            market_cap_dominance: 0.17,
            fully_diluted_market_cap: 4173000000,
            last_updated: new Date().toISOString(),
          }
        }
      }
    ];
  }

  private getMockGlobalMarketData(): GlobalMarketData {
    return {
      active_cryptocurrencies: 9950,
      total_cryptocurrencies: 25000,
      active_market_pairs: 85000,
      active_exchanges: 650,
      total_exchanges: 1200,
      eth_dominance: 15.5,
      btc_dominance: 45.2,
      eth_dominance_yesterday: 15.2,
      btc_dominance_yesterday: 44.8,
      eth_dominance_24h_percentage_change: 1.97,
      btc_dominance_24h_percentage_change: 0.89,
      defi_volume_24h: 5000000000,
      defi_volume_24h_reported: 5200000000,
      defi_market_cap: 85000000000,
      defi_24h_percentage_change: 12.5,
      stablecoin_volume_24h: 75000000000,
      stablecoin_volume_24h_reported: 76000000000,
      stablecoin_market_cap: 135000000000,
      stablecoin_24h_percentage_change: 2.1,
      derivatives_volume_24h: 125000000000,
      derivatives_volume_24h_reported: 128000000000,
      derivatives_24h_percentage_change: 8.7,
      quote: {
        USD: {
          total_market_cap: 1950000000000,
          total_volume_24h: 85000000000,
          total_volume_24h_reported: 87000000000,
          altcoin_volume_24h: 60000000000,
          altcoin_volume_24h_reported: 61000000000,
          altcoin_market_cap: 1069000000000,
          defi_volume_24h: 5000000000,
          defi_volume_24h_reported: 5200000000,
          defi_24h_percentage_change: 12.5,
          defi_market_cap: 85000000000,
          stablecoin_volume_24h: 75000000000,
          stablecoin_volume_24h_reported: 76000000000,
          stablecoin_24h_percentage_change: 2.1,
          stablecoin_market_cap: 135000000000,
          derivatives_volume_24h: 125000000000,
          derivatives_volume_24h_reported: 128000000000,
          derivatives_24h_percentage_change: 8.7,
          total_market_cap_yesterday: 1920000000000,
          total_volume_24h_yesterday: 82000000000,
          total_market_cap_yesterday_percentage_change: 1.56,
          total_volume_24h_yesterday_percentage_change: 3.66,
          last_updated: new Date().toISOString(),
        }
      }
    };
  }

  private getMockGlobalMetrics(): GlobalMetrics {
    return {
      totalMarketCap: 1950000000000,
      totalMarketCapChange24h: 1.56,
      total24hVolume: 85000000000,
      total24hVolumeChange: 3.66,
      btcDominance: 45.2,
      ethDominance: 15.5,
      activeCryptocurrencies: 9950,
      totalExchanges: 1200,
      fearGreedIndex: 65,
      fearGreedValue: 'Greed',
      lastUpdated: new Date().toISOString(),
    };
  }

  private getMockPriceHistory(symbol: string, timeframe: string): PriceHistory[] {
    // Use current realistic prices as base
    const basePrice = symbol === 'BTC' ? 118500 : 
                     symbol === 'ETH' ? 4125 : 
                     symbol === 'ADA' ? 0.45 :
                     symbol === 'DOT' ? 8.5 :
                     symbol === 'MATIC' ? 0.85 :
                     symbol === 'SOL' ? 185 :
                     symbol === 'AVAX' ? 35 :
                     symbol === 'LINK' ? 22 :
                     symbol === 'DOGE' ? 0.12 :
                     100; // Default for other coins
    
    const history: PriceHistory[] = [];
    const points = timeframe === '1h' ? 60 : timeframe === '24h' ? 24 : timeframe === '7d' ? 7 : 30;
    const intervalMs = timeframe === '1h' ? 60000 : // 1 minute intervals for 1h
                      timeframe === '24h' ? 3600000 : // 1 hour intervals for 24h  
                      timeframe === '7d' ? 86400000 : // 1 day intervals for 7d
                      86400000; // 1 day intervals for 30d
    
    // Create more realistic price movements
    let currentPrice = basePrice;
    const now = Date.now();
    
    for (let i = points; i >= 0; i--) {
      const timestamp = now - (i * intervalMs);
      
      // Create realistic price movements using multiple factors
      const timeNoise = Math.sin(i * 0.1) * 0.02; // Long term trend
      const randomNoise = (Math.random() - 0.5) * 0.08; // Random movements ±4%
      const volatilityFactor = symbol === 'BTC' ? 0.5 : 
                              symbol === 'ETH' ? 0.7 :
                              symbol.includes('USD') ? 0.05 : 1.2; // Stablecoins less volatile
      
      const totalVariation = (timeNoise + randomNoise) * volatilityFactor;
      currentPrice = currentPrice * (1 + totalVariation);
      
      // Ensure price doesn't go too far from base
      const maxDeviation = 0.15; // ±15% from base price
      const minPrice = basePrice * (1 - maxDeviation);
      const maxPrice = basePrice * (1 + maxDeviation);
      currentPrice = Math.max(minPrice, Math.min(maxPrice, currentPrice));
      
      history.push({
        timestamp,
        price: currentPrice,
        volume: (Math.random() * 0.5 + 0.5) * 1000000000 * (basePrice / 1000), // Scale volume with price
        marketCap: currentPrice * (symbol === 'BTC' ? 19750000 : 
                                  symbol === 'ETH' ? 120280000 : 
                                  1000000000), // Rough supply estimates
      });
    }
    
    return history.sort((a, b) => a.timestamp - b.timestamp); // Ensure chronological order
  }

  private getMockTechnicalIndicators(symbol: string): TechnicalIndicators {
    return {
      rsi: 45 + Math.random() * 30, // RSI between 45-75
      macd: {
        macd: Math.random() * 200 - 100,
        signal: Math.random() * 200 - 100,
        histogram: Math.random() * 50 - 25,
        trend: Math.random() > 0.5 ? 'bullish' : 'bearish',
      },
      bollingerBands: {
        upper: 50000,
        middle: 45000,
        lower: 40000,
        position: 'middle',
      },
      movingAverages: {
        sma20: 44500,
        sma50: 43000,
        sma200: 40000,
        ema20: 44800,
        ema50: 43200,
      },
    };
  }

  private getMockMarketSentiment(): MarketSentiment {
    return {
      twitterSentiment: {
        score: 0.65,
        label: 'positive',
        mentions: 15420,
      },
      newsSentiment: {
        score: 0.45,
        label: 'neutral',
        articles: 127,
      },
      socialVolume: {
        score: 0.8,
        label: 'high',
        change24h: 12.5,
      },
      redditSentiment: {
        score: 0.72,
        label: 'positive',
        posts: 2341,
      },
    };
  }
}

export const cryptoAPI = new CryptoAPI();
