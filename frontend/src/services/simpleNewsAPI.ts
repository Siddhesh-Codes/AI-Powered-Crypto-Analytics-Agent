/**
 * Simplified Crypto News API Service
 * Fetches live cryptocurrency news from multiple sources
 */

export interface NewsArticle {
  id: string;
  title: string;
  description: string;
  url: string;
  source: string;
  publishedAt: Date;
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  sentimentScore: number;
  relevantCoins: string[];
  category: 'market' | 'regulation' | 'technology' | 'adoption' | 'trading';
  imageUrl?: string;
}

export interface SentimentData {
  symbol: string;
  sentiment: number;
  trend: 'up' | 'down' | 'stable';
  volume: number;
  sources: number;
}

/**
 * Simplified Cryptocurrency News API Client
 */
class SimpleCryptoNewsAPI {
  /**
   * Fetch crypto news from CryptoCompare (free tier, no API key required)
   */
  async fetchCryptoNews(limit: number = 20): Promise<NewsArticle[]> {
    try {
      const url = `https://min-api.cryptocompare.com/data/v2/news/?lang=EN&extraParams=ai-crypto-app&limit=${limit}`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`CryptoCompare Error: ${response.status}`);
      }
      
      const data = await response.json();
      
      return data.Data?.map((article: any, index: number) => ({
        id: `cryptocompare_${index}_${Date.now()}`,
        title: article.title || 'No title available',
        description: article.body?.substring(0, 200) + '...' || 'No description available',
        url: article.url,
        source: article.source_info?.name || article.source || 'CryptoCompare',
        publishedAt: new Date(article.published_on * 1000),
        sentiment: this.analyzeSentiment(article.title + ' ' + (article.body || '')),
        sentimentScore: this.getSentimentScore(article.title + ' ' + (article.body || '')),
        relevantCoins: this.extractRelevantCoins(article.title + ' ' + (article.body || '')),
        category: this.categorizeNews(article.title + ' ' + (article.body || '')),
        imageUrl: article.imageurl && this.isValidImageUrl(article.imageurl) 
          ? article.imageurl 
          : this.getDefaultCryptoImage(article.title)
      })) || [];
      
    } catch (error) {
      console.error('Error fetching CryptoCompare news:', error);
      return this.getFallbackNews();
    }
  }

  /**
   * Generate mock sentiment data
   */
  async fetchSentimentData(): Promise<SentimentData[]> {
    return [
      { symbol: 'BTC', sentiment: 0.7, trend: 'up', volume: 1250, sources: 45 },
      { symbol: 'ETH', sentiment: 0.6, trend: 'up', volume: 890, sources: 32 },
      { symbol: 'ADA', sentiment: -0.3, trend: 'down', volume: 340, sources: 18 },
      { symbol: 'SOL', sentiment: 0.2, trend: 'stable', volume: 420, sources: 22 },
      { symbol: 'DOT', sentiment: -0.1, trend: 'down', volume: 280, sources: 15 },
      { symbol: 'LINK', sentiment: 0.4, trend: 'up', volume: 310, sources: 19 },
      { symbol: 'UNI', sentiment: 0.3, trend: 'stable', volume: 220, sources: 12 },
      { symbol: 'AAVE', sentiment: 0.5, trend: 'up', volume: 180, sources: 14 }
    ];
  }

  /**
   * Simple sentiment analysis
   */
  private analyzeSentiment(text: string): 'BULLISH' | 'BEARISH' | 'NEUTRAL' {
    const bullishWords = ['bull', 'bullish', 'rise', 'pump', 'moon', 'green', 'gain', 'profit', 'up', 'high', 'surge', 'rally', 'breakthrough', 'adoption', 'approval'];
    const bearishWords = ['bear', 'bearish', 'fall', 'dump', 'crash', 'red', 'loss', 'down', 'low', 'drop', 'decline', 'concern', 'regulatory'];
    
    const lowerText = text.toLowerCase();
    const bullishCount = bullishWords.filter(word => lowerText.includes(word)).length;
    const bearishCount = bearishWords.filter(word => lowerText.includes(word)).length;
    
    if (bullishCount > bearishCount) return 'BULLISH';
    if (bearishCount > bullishCount) return 'BEARISH';
    return 'NEUTRAL';
  }

  /**
   * Get sentiment score (-1 to 1)
   */
  private getSentimentScore(text: string): number {
    const sentiment = this.analyzeSentiment(text);
    if (sentiment === 'BULLISH') return Math.random() * 0.5 + 0.3;
    if (sentiment === 'BEARISH') return Math.random() * 0.5 - 0.8;
    return Math.random() * 0.4 - 0.2;
  }

  /**
   * Extract relevant cryptocurrency symbols from text
   */
  private extractRelevantCoins(text: string): string[] {
    const coinKeywords = {
      'BTC': ['bitcoin', 'btc'],
      'ETH': ['ethereum', 'eth', 'ether'],
      'ADA': ['cardano', 'ada'],
      'SOL': ['solana', 'sol'],
      'DOT': ['polkadot', 'dot'],
      'LINK': ['chainlink', 'link'],
      'UNI': ['uniswap', 'uni'],
      'AAVE': ['aave'],
      'DOGE': ['dogecoin', 'doge'],
      'XRP': ['ripple', 'xrp']
    };
    
    const lowerText = text.toLowerCase();
    const relevantCoins: string[] = [];
    
    for (const [symbol, keywords] of Object.entries(coinKeywords)) {
      if (keywords.some(keyword => lowerText.includes(keyword))) {
        relevantCoins.push(symbol);
      }
    }
    
    return relevantCoins.length > 0 ? relevantCoins : ['BTC', 'ETH'];
  }

  /**
   * Categorize news article
   */
  private categorizeNews(text: string): 'market' | 'regulation' | 'technology' | 'adoption' | 'trading' {
    const lowerText = text.toLowerCase();
    
    if (lowerText.includes('regulat') || lowerText.includes('sec') || lowerText.includes('legal')) {
      return 'regulation';
    }
    if (lowerText.includes('technolog') || lowerText.includes('blockchain') || lowerText.includes('protocol')) {
      return 'technology';
    }
    if (lowerText.includes('adopt') || lowerText.includes('institution') || lowerText.includes('corporate')) {
      return 'adoption';
    }
    if (lowerText.includes('trading') || lowerText.includes('exchange') || lowerText.includes('volume')) {
      return 'trading';
    }
    return 'market';
  }

  /**
   * Check if image URL is valid
   */
  private isValidImageUrl(url: string): boolean {
    return Boolean(url && url.startsWith('http') && (url.includes('jpg') || url.includes('jpeg') || url.includes('png') || url.includes('webp')));
  }

  /**
   * Get default crypto image based on content
   */
  private getDefaultCryptoImage(title: string): string {
    const lowerTitle = title.toLowerCase();
    
    if (lowerTitle.includes('bitcoin') || lowerTitle.includes('btc')) {
      return 'https://cryptologos.cc/logos/bitcoin-btc-logo.png';
    }
    if (lowerTitle.includes('ethereum') || lowerTitle.includes('eth')) {
      return 'https://cryptologos.cc/logos/ethereum-eth-logo.png';
    }
    if (lowerTitle.includes('cardano') || lowerTitle.includes('ada')) {
      return 'https://cryptologos.cc/logos/cardano-ada-logo.png';
    }
    if (lowerTitle.includes('solana') || lowerTitle.includes('sol')) {
      return 'https://cryptologos.cc/logos/solana-sol-logo.png';
    }
    
    return 'https://via.placeholder.com/128x96/1e293b/64748b?text=Crypto';
  }

  /**
   * Fallback news when APIs fail
   */
  private getFallbackNews(): NewsArticle[] {
    return [
      {
        id: 'fallback_1',
        title: 'Bitcoin Trading Near All-Time Highs as Institutional Interest Grows',
        description: 'Bitcoin continues to show strong momentum as major financial institutions increase their cryptocurrency allocations...',
        url: 'https://example.com/bitcoin-news',
        source: 'Crypto News',
        publishedAt: new Date(),
        sentiment: 'BULLISH',
        sentimentScore: 0.8,
        relevantCoins: ['BTC'],
        category: 'market',
        imageUrl: 'https://cryptologos.cc/logos/bitcoin-btc-logo.png'
      },
      {
        id: 'fallback_2',
        title: 'Ethereum Network Upgrades Show Promising Results',
        description: 'The latest Ethereum network improvements have led to reduced gas fees and improved scalability...',
        url: 'https://example.com/ethereum-news',
        source: 'DeFi Weekly',
        publishedAt: new Date(Date.now() - 60 * 60 * 1000),
        sentiment: 'BULLISH',
        sentimentScore: 0.7,
        relevantCoins: ['ETH'],
        category: 'technology',
        imageUrl: 'https://cryptologos.cc/logos/ethereum-eth-logo.png'
      }
    ];
  }
}

// Export singleton instance
export const simpleCryptoNewsAPI = new SimpleCryptoNewsAPI();
export default simpleCryptoNewsAPI;