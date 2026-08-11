"""
Test Suite 7: News Sentiment Analysis Tests
Tests NewsAPIClient and SentimentAnalyzer
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestNewsSentiment:
    """Test news and sentiment modules"""

    def test_newsapi_client_init(self):
        """TC-7.1: NewsAPIClient initializes correctly"""
        from news_sentiment import NewsAPIClient
        client = NewsAPIClient()
        assert client.base_url == "https://newsapi.org/v2"
        assert isinstance(client.crypto_keywords, list)
        assert len(client.crypto_keywords) > 0

    @pytest.mark.asyncio
    async def test_get_mock_news(self):
        """TC-7.2: Mock news returns articles when no API key"""
        from news_sentiment import NewsAPIClient
        client = NewsAPIClient()
        client.news_api_key = ""  # Force mock mode
        news = await client.get_crypto_news(limit=5)
        assert isinstance(news, list)
        assert len(news) > 0

    @pytest.mark.asyncio
    async def test_mock_news_article_structure(self):
        """TC-7.3: Mock news articles have required fields"""
        from news_sentiment import NewsAPIClient
        client = NewsAPIClient()
        client.news_api_key = ""
        news = await client.get_crypto_news(limit=3)
        if news:
            article = news[0]
            assert "title" in article
            assert "source" in article

    def test_sentiment_analyzer_init(self):
        """TC-7.4: SentimentAnalyzer initializes"""
        from news_sentiment import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        assert analyzer is not None

    @pytest.mark.asyncio
    async def test_analyze_market_sentiment(self):
        """TC-7.5: Market sentiment analysis returns structured data"""
        from news_sentiment import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        # analyze_market_sentiment requires articles argument
        mock_articles = [
            {
                "title": "Bitcoin surges past $100k",
                "sentiment": {"label": "positive", "polarity": 0.6, "confidence": 0.7},
                "relevance_score": 0.8
            },
            {
                "title": "Crypto market uncertain",
                "sentiment": {"label": "neutral", "polarity": 0.0, "confidence": 0.3},
                "relevance_score": 0.5
            }
        ]
        result = analyzer.analyze_market_sentiment(mock_articles)
        assert isinstance(result, dict)
        assert "overall_sentiment" in result
        assert "sentiment_score" in result or "article_count" in result

    def test_process_article_sentiment(self):
        """TC-7.6: Article sentiment analysis returns structured result"""
        from news_sentiment import NewsAPIClient
        client = NewsAPIClient()
        sentiment = client._analyze_sentiment("Bitcoin price surges to new all-time high, bulls are dominating")
        # _analyze_sentiment returns a dict with label, polarity, subjectivity, confidence
        assert isinstance(sentiment, dict)
        assert "label" in sentiment
        assert sentiment["label"] in ["positive", "negative", "neutral"]
        assert "polarity" in sentiment
        assert isinstance(sentiment["polarity"], (int, float))

    def test_extract_crypto_mentions(self):
        """TC-7.7: Crypto mentions are extracted from text"""
        from news_sentiment import NewsAPIClient
        client = NewsAPIClient()
        mentions = client._extract_crypto_mentions("Bitcoin and Ethereum lead the crypto market rally")
        assert isinstance(mentions, list)
        assert len(mentions) > 0

    def test_calculate_relevance_score(self):
        """TC-7.8: Relevance score is calculated"""
        from news_sentiment import NewsAPIClient
        client = NewsAPIClient()
        score = client._calculate_relevance_score("Bitcoin hits $100k milestone, crypto market celebrates")
        assert isinstance(score, (int, float))
        assert score >= 0
