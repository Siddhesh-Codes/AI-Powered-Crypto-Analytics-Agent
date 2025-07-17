import React, { useState, useEffect } from 'react';
import { Newspaper, TrendingUp, TrendingDown, Heart, MessageCircle, Share2, Clock, ExternalLink } from 'lucide-react';

interface NewsArticle {
  id: string;
  title: string;
  description: string;
  url: string;
  source: string;
  publishedAt: Date;
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  sentimentScore: number; // -1 to 1
  relevantCoins: string[];
  category: 'market' | 'regulation' | 'technology' | 'adoption' | 'trading';
  imageUrl?: string;
}

interface SentimentData {
  symbol: string;
  sentiment: number; // -1 to 1
  trend: 'up' | 'down' | 'stable';
  volume: number;
  sources: number;
}

/**
 * Advanced News & Sentiment Analysis Component
 * Real-time crypto news with AI sentiment analysis
 */
const NewsAndSentiment: React.FC = () => {
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [sentiment, setSentiment] = useState<SentimentData[]>([]);
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  // Simulate news data (in real app, would fetch from news APIs)
  useEffect(() => {
    const generateMockNews = (): NewsArticle[] => [
      {
        id: '1',
        title: 'Bitcoin ETF Approval Drives Institutional Adoption',
        description: 'Major financial institutions are increasing their Bitcoin exposure following recent regulatory clarity...',
        url: 'https://example.com/news/1',
        source: 'CryptoNews',
        publishedAt: new Date(Date.now() - 1000 * 60 * 30), // 30 min ago
        sentiment: 'BULLISH',
        sentimentScore: 0.8,
        relevantCoins: ['BTC', 'ETH'],
        category: 'regulation',
        imageUrl: 'https://via.placeholder.com/400x200/1a1a2e/eee?text=Bitcoin+ETF'
      },
      {
        id: '2',
        title: 'Ethereum 2.0 Staking Rewards Reach New Highs',
        description: 'Ethereum staking yields continue to attract investors as the network processes record transactions...',
        url: 'https://example.com/news/2',
        source: 'DeFi Pulse',
        publishedAt: new Date(Date.now() - 1000 * 60 * 60), // 1 hour ago
        sentiment: 'BULLISH',
        sentimentScore: 0.7,
        relevantCoins: ['ETH'],
        category: 'technology',
        imageUrl: 'https://via.placeholder.com/400x200/16213e/eee?text=Ethereum+2.0'
      },
      {
        id: '3',
        title: 'Regulatory Concerns Impact Altcoin Markets',
        description: 'New regulatory proposals in major markets are causing uncertainty in the altcoin space...',
        url: 'https://example.com/news/3',
        source: 'Blockchain Today',
        publishedAt: new Date(Date.now() - 1000 * 60 * 90), // 1.5 hours ago
        sentiment: 'BEARISH',
        sentimentScore: -0.6,
        relevantCoins: ['ADA', 'SOL', 'DOT'],
        category: 'regulation',
        imageUrl: 'https://via.placeholder.com/400x200/4a1e1e/eee?text=Regulation+News'
      },
      {
        id: '4',
        title: 'DeFi Protocol Launches Revolutionary Yield Farming',
        description: 'A new DeFi protocol promises sustainable high yields through innovative tokenomics...',
        url: 'https://example.com/news/4',
        source: 'DeFi Weekly',
        publishedAt: new Date(Date.now() - 1000 * 60 * 120), // 2 hours ago
        sentiment: 'BULLISH',
        sentimentScore: 0.5,
        relevantCoins: ['UNI', 'SUSHI', 'AAVE'],
        category: 'technology',
        imageUrl: 'https://via.placeholder.com/400x200/1e4a2e/eee?text=DeFi+Innovation'
      },
      {
        id: '5',
        title: 'Major Corporation Adds Bitcoin to Treasury',
        description: 'Another Fortune 500 company announces Bitcoin treasury allocation, following corporate adoption trend...',
        url: 'https://example.com/news/5',
        source: 'Corporate Crypto',
        publishedAt: new Date(Date.now() - 1000 * 60 * 180), // 3 hours ago
        sentiment: 'BULLISH',
        sentimentScore: 0.9,
        relevantCoins: ['BTC'],
        category: 'adoption',
        imageUrl: 'https://via.placeholder.com/400x200/2e1e4a/eee?text=Corporate+Adoption'
      }
    ];

    const generateSentimentData = (): SentimentData[] => [
      { symbol: 'BTC', sentiment: 0.7, trend: 'up', volume: 1250, sources: 45 },
      { symbol: 'ETH', sentiment: 0.6, trend: 'up', volume: 890, sources: 32 },
      { symbol: 'ADA', sentiment: -0.3, trend: 'down', volume: 340, sources: 18 },
      { symbol: 'SOL', sentiment: 0.2, trend: 'stable', volume: 420, sources: 22 },
      { symbol: 'DOT', sentiment: -0.1, trend: 'down', volume: 280, sources: 15 },
      { symbol: 'LINK', sentiment: 0.4, trend: 'up', volume: 310, sources: 19 },
      { symbol: 'UNI', sentiment: 0.3, trend: 'stable', volume: 220, sources: 12 },
      { symbol: 'AAVE', sentiment: 0.5, trend: 'up', volume: 180, sources: 14 }
    ];

    setNews(generateMockNews());
    setSentiment(generateSentimentData());
    setLoading(false);
  }, []);

  const categories = [
    { id: 'all', label: 'All News', icon: '📰' },
    { id: 'market', label: 'Market', icon: '📈' },
    { id: 'regulation', label: 'Regulation', icon: '⚖️' },
    { id: 'technology', label: 'Technology', icon: '🔧' },
    { id: 'adoption', label: 'Adoption', icon: '🏢' },
    { id: 'trading', label: 'Trading', icon: '💹' }
  ];

  const filteredNews = activeCategory === 'all' 
    ? news 
    : news.filter(article => article.category === activeCategory);

  const getSentimentColor = (sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL') => {
    switch (sentiment) {
      case 'BULLISH': return 'text-green-400 bg-green-900/20';
      case 'BEARISH': return 'text-red-400 bg-red-900/20';
      case 'NEUTRAL': return 'text-yellow-400 bg-yellow-900/20';
    }
  };

  const getSentimentIcon = (sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL') => {
    switch (sentiment) {
      case 'BULLISH': return <TrendingUp className="w-4 h-4" />;
      case 'BEARISH': return <TrendingDown className="w-4 h-4" />;
      case 'NEUTRAL': return <Heart className="w-4 h-4" />;
    }
  };

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  const getSentimentBarColor = (sentiment: number) => {
    if (sentiment > 0.3) return 'bg-green-500';
    if (sentiment > -0.3) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="p-6 text-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-slate-400">Loading news and sentiment data...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold gradient-text flex items-center mb-2">
          <Newspaper className="w-8 h-8 mr-3 text-blue-400" />
          News & Sentiment Analysis
        </h2>
        <p className="text-slate-400">Real-time crypto news with AI-powered sentiment analysis</p>
      </div>

      {/* Sentiment Overview */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Heart className="w-5 h-5 mr-2 text-purple-400" />
          Market Sentiment Overview
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {sentiment.slice(0, 8).map(item => (
            <div key={item.symbol} className="bg-slate-700 p-3 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-slate-200">{item.symbol}</span>
                <span className={`text-sm ${item.sentiment > 0 ? 'text-green-400' : item.sentiment < 0 ? 'text-red-400' : 'text-yellow-400'}`}>
                  {item.trend === 'up' ? '↗️' : item.trend === 'down' ? '↘️' : '➡️'}
                </span>
              </div>
              
              <div className="mb-2">
                <div className="w-full h-2 bg-slate-600 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${getSentimentBarColor(item.sentiment)}`}
                    style={{ width: `${Math.abs(item.sentiment) * 100}%` }}
                  />
                </div>
              </div>
              
              <div className="flex justify-between text-xs text-slate-400">
                <span>{item.volume} mentions</span>
                <span>{item.sources} sources</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map(category => (
          <button
            key={category.id}
            onClick={() => setActiveCategory(category.id)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              activeCategory === category.id
                ? 'bg-blue-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            <span>{category.icon}</span>
            <span>{category.label}</span>
          </button>
        ))}
      </div>

      {/* News Articles */}
      <div className="space-y-4">
        {filteredNews.map(article => (
          <div key={article.id} className="card hover:bg-slate-750 transition-colors">
            <div className="flex space-x-4">
              {/* Article Image */}
              {article.imageUrl && (
                <div className="flex-shrink-0 w-32 h-24 bg-slate-700 rounded-lg overflow-hidden">
                  <img 
                    src={article.imageUrl} 
                    alt={article.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              
              {/* Article Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-semibold text-slate-200 line-clamp-2 pr-4">
                    {article.title}
                  </h3>
                  
                  <div className={`flex items-center space-x-1 px-2 py-1 rounded-lg text-sm font-medium ${getSentimentColor(article.sentiment)}`}>
                    {getSentimentIcon(article.sentiment)}
                    <span>{article.sentiment}</span>
                  </div>
                </div>
                
                <p className="text-slate-400 text-sm mb-3 line-clamp-2">
                  {article.description}
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-slate-500">
                    <span className="flex items-center">
                      <Clock className="w-4 h-4 mr-1" />
                      {formatTimeAgo(article.publishedAt)}
                    </span>
                    <span>{article.source}</span>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    {/* Relevant Coins */}
                    <div className="flex space-x-1">
                      {article.relevantCoins.map(coin => (
                        <span
                          key={coin}
                          className="px-2 py-1 bg-slate-600 text-xs rounded text-slate-300"
                        >
                          {coin}
                        </span>
                      ))}
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex space-x-2">
                      <button className="p-1 hover:bg-slate-600 rounded text-slate-400 hover:text-slate-300">
                        <MessageCircle className="w-4 h-4" />
                      </button>
                      <button className="p-1 hover:bg-slate-600 rounded text-slate-400 hover:text-slate-300">
                        <Share2 className="w-4 h-4" />
                      </button>
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1 hover:bg-slate-600 rounded text-slate-400 hover:text-slate-300"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Load More */}
      <div className="text-center">
        <button className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
          Load More News
        </button>
      </div>
    </div>
  );
};

export default NewsAndSentiment;
