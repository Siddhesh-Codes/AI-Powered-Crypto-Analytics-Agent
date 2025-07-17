import React from 'react';
import NewsAndSentiment from '../components/News/NewsAndSentiment';

/**
 * News Page - Crypto News & Sentiment Analysis
 */
const NewsPage: React.FC = () => {
  return (
    <div className="p-6">
      <NewsAndSentiment />
    </div>
  );
};

export default NewsPage;
