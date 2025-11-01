import React from 'react';
import NewsAndSentiment from '../components/News';

/**
 * News Page - Crypto News & Sentiment Analysis
 */
const NewsPage: React.FC = () => {
  return (
    <div className="p-6 min-h-full overflow-y-auto">
      <NewsAndSentiment />
    </div>
  );
};

export default NewsPage;
