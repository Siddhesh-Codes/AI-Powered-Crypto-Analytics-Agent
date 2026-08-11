<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# AI-Powered Crypto Analytics Agent - Copilot Instructions

This is a comprehensive full-stack cryptocurrency analytics application with AI-powered forecasting capabilities.

## Project Context

### Technology Stack
- **Frontend**: React 18 with TypeScript, Tailwind CSS, Chart.js for visualizations
- **Backend**: Python FastAPI for AI/ML, Node.js for real-time features
- **Database**: PostgreSQL for data storage, Redis for caching
- **AI/ML**: TensorFlow/Keras (LSTM), Statsmodels (ARIMA), Transformers, NLTK (sentiment)

### Key Features
- Real-time cryptocurrency price tracking and analysis
- AI-powered price forecasting using LSTM, ARIMA, and Transformer models
- Technical analysis indicators (RSI, MACD, Bollinger Bands)
- Market sentiment analysis from social media and news
- User authentication and portfolio management
- Risk assessment and trading signals
- Real-time notifications and alerts

### Code Style Guidelines
- Use TypeScript for all frontend code with strict typing
- Follow React functional components with hooks pattern
- Use async/await for all asynchronous operations
- Implement proper error handling and user feedback
- Use descriptive variable and function names
- Add comprehensive JSDoc comments for functions
- Follow REST API conventions for backend endpoints
- Use proper database relationships and indexing

### AI/ML Specific Instructions
- LSTM models should handle time series data with proper preprocessing
- ARIMA models should include stationarity testing and parameter optimization
- Implement proper train/validation/test splits for all models
- Use cross-validation for model evaluation
- Include model performance metrics and logging
- Implement real-time prediction capabilities
- Handle missing data and outliers appropriately

### Security Considerations
- Implement JWT-based authentication
- Use bcrypt for password hashing
- Validate all user inputs
- Implement rate limiting for API endpoints
- Use HTTPS for all communications
- Sanitize database queries to prevent injection

### Performance Optimization
- Implement efficient caching strategies
- Use database indexing for frequently queried data
- Optimize API response times
- Implement lazy loading for frontend components
- Use WebSocket for real-time data updates
- Minimize bundle size with code splitting

### Free Tier Constraints
- Use free APIs (CoinMarketCap free tier, NewsAPI free tier)
- Optimize API calls to stay within rate limits
- Implement intelligent caching to reduce API usage
- Design for deployment on free hosting platforms (Vercel, Netlify, Railway)

### Testing Requirements
- Unit tests for all utility functions
- Integration tests for API endpoints
- Component tests for React components
- Model accuracy tests for AI/ML components
- End-to-end tests for critical user flows

When writing code for this project, prioritize:
1. Type safety and error handling
2. Performance and scalability
3. User experience and accessibility
4. Code maintainability and documentation
5. Security best practices
6. Cost-effective solutions (free tier optimizations)
