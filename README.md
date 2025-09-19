# 🚀 AI-Powered Crypto Analytics Application

[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=flat&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9.5-3178C6?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

A comprehensive full-stack cryptocurrency analytics application with **AI-powered forecasting capabilities**, **real-time market analysis**, and **intelligent trading signals**. Built as a Final Year Project showcasing modern web development, machine learning, and financial technology integration.

## ✨ Key Features

### 🤖 **AI-Powered Analytics**
- **Multi-Model Forecasting**: LSTM, ARIMA, and Transformer models for price prediction
- **Intelligent Chat Assistant**: Powered by Groq API for market insights and Q&A
- **Technical Analysis**: RSI, MACD, Bollinger Bands, and custom indicators
- **Market Sentiment Analysis**: Real-time sentiment from news and social media

### 📊 **Real-Time Trading Tools**
- **Live Price Monitoring**: Real-time cryptocurrency price tracking
- **Trading Signals**: AI-generated buy/sell recommendations
- **Risk Assessment**: Portfolio risk analysis and management
- **Custom Alerts**: Price alerts and notification system

### 🔐 **User Management**
- **Secure Authentication**: JWT-based auth with OTP verification
- **Portfolio Tracking**: Multi-currency portfolio management
- **User Profiles**: Personalized settings and preferences
- **Trading History**: Complete transaction and analysis history

### 📱 **Modern UI/UX**
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Interactive Charts**: Advanced charting with Chart.js and Recharts
- **Real-time Updates**: WebSocket integration for live data
- **Dark/Light Themes**: Customizable user interface

## 🛠️ Technology Stack

### **Frontend Architecture**
- **React 18** with TypeScript for type-safe development
- **Tailwind CSS** for modern, responsive styling
- **Chart.js & Recharts** for advanced data visualizations
- **Zustand** for efficient state management
- **React Query** for server state management
- **Framer Motion** for smooth animations
- **React Router** for client-side routing

### **Backend Infrastructure**
- **FastAPI** for high-performance API development
- **SQLAlchemy** for database ORM and migrations
- **SQLite/PostgreSQL** for data persistence
- **WebSocket** for real-time communication
- **JWT & BCrypt** for secure authentication
- **Uvicorn** as ASGI server

### **AI/ML & Data Processing**
- **Groq API** for advanced language model capabilities
- **TensorFlow/Keras** for LSTM neural networks
- **Statsmodels** for ARIMA time series analysis
- **NumPy & Pandas** for data manipulation
- **TextBlob & NLTK** for sentiment analysis
- **Technical Indicators** custom implementation

### **External APIs & Services**
- **CoinMarketCap API** for cryptocurrency data
- **News API** for market news and sentiment
- **Email Services** for OTP and notifications
- **WebSocket APIs** for real-time price feeds

## 🚀 Quick Start Guide

### **Prerequisites**
- **Node.js** (v16 or higher) - [Download here](https://nodejs.org/)
- **Python** (v3.8 or higher) - [Download here](https://www.python.org/)
- **Git** - [Download here](https://git-scm.com/)
- **PostgreSQL** (optional, uses SQLite by default) - [Download here](https://www.postgresql.org/)

### **1. Clone the Repository**
```bash
git clone https://github.com/Siddhesh-Codes/ai-crypto-analytics.git
cd "AI Powered Crypto Application"
```

### **2. Quick Installation (Recommended)**
Use the automated installation scripts:

```bash
# Install all dependencies for both frontend and backend
npm run install:all

# Start the complete development environment
npm run dev
```

### **3. Manual Installation**

#### **Backend Setup**
```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Initialize database
python setup_database.py

# Start backend server
python simple_backend.py
```

#### **Frontend Setup**
```bash
cd frontend

# Install Node.js dependencies
npm install

# Start frontend development server
npm start
```

### **4. Environment Configuration**

#### **Backend Environment Variables**
Create a `.env` file in the `backend` directory:

```env
# 🔑 API Keys (Get your free keys from respective providers)
GROQ_API_KEY=your_groq_api_key_here
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key_here
NEWS_API_KEY=your_news_api_key_here

# 📧 Email Configuration for OTP
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password

# 🗄️ Database Configuration
DATABASE_URL=sqlite:///./crypto_analytics.db
# For PostgreSQL: postgresql://username:password@localhost/dbname

# 🔐 Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 🌐 CORS Settings
FRONTEND_URL=http://localhost:3000
```

#### **Frontend Environment Variables**
Create a `.env` file in the `frontend` directory:

```env
# 🔗 API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000

# 🔑 Public API Keys (if needed)
REACT_APP_COINMARKETCAP_API_KEY=your_public_api_key_here
```

### **5. Get Your API Keys**

| Service | Purpose | Free Tier | Sign Up Link |
|---------|---------|-----------|--------------|
| **Groq** | AI Chat Assistant | ✅ Yes | [groq.com](https://groq.com) |
| **CoinMarketCap** | Crypto Data | ✅ 10,000 calls/month | [coinmarketcap.com/api](https://coinmarketcap.com/api/) |
| **NewsAPI** | Market News | ✅ 1,000 requests/day | [newsapi.org](https://newsapi.org/) |
| **Gmail App Password** | OTP Email | ✅ Free | [Google Account Settings](https://myaccount.google.com/apppasswords) |

## �️ Application Usage

### **Development Mode**
```bash
# Start both frontend and backend simultaneously
npm run dev

# Or start them separately:
npm run dev:frontend  # Frontend only (port 3000)
npm run dev:backend   # Backend only (port 8000)
```

### **Available Scripts**
| Command | Description |
|---------|-------------|
| `npm run install:all` | Install dependencies for both frontend and backend |
| `npm run dev` | Start both frontend and backend |
| `npm run dev:frontend` | Start frontend development server |
| `npm run dev:backend` | Start backend API server |
| `npm run build:frontend` | Build frontend for production |
| `npm test` | Run all tests |

### **Access Points**
- **Frontend Application**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🏗️ Project Structure

```
AI Powered Crypto Application/
├── 📁 frontend/                 # React TypeScript Frontend
│   ├── 📁 src/
│   │   ├── 📁 components/       # Reusable UI components
│   │   │   ├── 📁 AI/           # AI chat and prediction components
│   │   │   ├── 📁 Auth/         # Authentication components
│   │   │   ├── 📁 Charts/       # Chart visualization components
│   │   │   ├── 📁 Crypto/       # Cryptocurrency data components
│   │   │   ├── 📁 Layout/       # Layout and navigation components
│   │   │   ├── 📁 News/         # News and sentiment components
│   │   │   └── 📁 Trading/      # Trading signals and alerts
│   │   ├── 📁 pages/            # Main application pages
│   │   ├── � services/         # API service layers
│   │   ├── 📁 hooks/            # Custom React hooks
│   │   ├── 📁 contexts/         # React context providers
│   │   ├── 📁 store/            # State management
│   │   └── 📁 utils/            # Utility functions
│   └── 📄 package.json          # Frontend dependencies
│
├── 📁 backend/                  # FastAPI Python Backend
│   ├── 📁 app/                  # Application core
│   │   ├── 📁 api/              # API routes and endpoints
│   │   └── 📁 services/         # Business logic services
│   ├── 📄 simple_backend.py     # Main application server
│   ├── 📄 models.py             # Database models
│   ├── 📄 database.py           # Database configuration
│   ├── 📄 auth_utils.py         # Authentication utilities
│   ├── 📄 technical_indicators.py # Trading indicators
│   ├── 📄 news_sentiment.py     # Sentiment analysis
│   └── 📄 requirements.txt      # Python dependencies
│
├── 📁 ai-models/                # AI/ML Model Implementations
│   ├── 📁 lstm/                 # LSTM neural network models
│   │   └── 📄 lstm_predictor.py
│   └── 📁 arima/                # ARIMA time series models
│       └── 📄 arima_predictor.py
│
├── 📄 package.json              # Root package.json for scripts
├── 📄 README.md                 # Project documentation
├── 📄 start-frontend.bat        # Windows batch scripts
└── 📄 start-backend.bat         # for easy development
```

## 🧪 AI/ML Model Training

### **LSTM Price Prediction Model**
```bash
# Train LSTM model for cryptocurrency price forecasting
python ai-models/lstm/lstm_predictor.py

# Or use the task runner
npm run train:lstm
```

### **ARIMA Time Series Model**
```bash
# Train ARIMA model for time series analysis
python ai-models/arima/arima_predictor.py

# Or use the task runner
npm run train:arima
```

### **Model Features**
- **LSTM Neural Networks**: Deep learning for complex pattern recognition
- **ARIMA Models**: Statistical time series forecasting
- **Technical Indicators**: RSI, MACD, Bollinger Bands integration
- **Sentiment Analysis**: News and social media sentiment scoring
- **Risk Assessment**: Portfolio risk calculation and optimization

## 🔒 Security & Best Practices

### **Environment Security**
```bash
# ❌ NEVER commit these files
.env
.env.local
.env.production

# ✅ Always use .env.example for documentation
.env.example
```

### **Security Checklist**
- ✅ JWT token-based authentication
- ✅ Password hashing with bcrypt
- ✅ Rate limiting on API endpoints
- ✅ Input validation and sanitization
- ✅ CORS configuration
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ Secure HTTP headers

### **API Key Management**
1. **Obtain API keys** from respective providers
2. **Store securely** in `.env` files
3. **Never commit** API keys to version control
4. **Rotate keys** if accidentally exposed
5. **Use environment variables** in production

## 🧪 Testing

### **Run All Tests**
```bash
npm test                    # Run all tests
npm run test:frontend      # Frontend tests only
npm run test:backend       # Backend tests only
```

### **Test Coverage**
- **Unit Tests**: Component and function testing
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Full user flow testing
- **AI Model Tests**: Model accuracy and performance

## 🚀 Deployment

### **Production Build**
```bash
# Build frontend for production
npm run build:frontend

# The build folder is ready to deploy
# Serve the backend with production ASGI server
```

### **Deployment Platforms**
- **Frontend**: Vercel, Netlify, Surge
- **Backend**: Railway, Heroku, DigitalOcean
- **Database**: PostgreSQL on Heroku, PlanetScale
- **Static Assets**: Cloudinary, AWS S3

## 📊 Features Showcase

### **Dashboard Analytics**
- Real-time cryptocurrency price charts
- Portfolio performance tracking
- Market sentiment indicators
- AI-powered trading signals

### **AI Chat Assistant**
- Natural language crypto market queries
- Intelligent analysis and recommendations
- Historical data insights
- Market trend explanations

### **Portfolio Management**
- Multi-currency portfolio tracking
- Profit/loss calculations
- Risk assessment metrics
- Performance analytics

### **Advanced Trading Tools**
- Technical indicator overlays
- Custom alert systems
- Automated trading signals
- Risk management tools

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes with proper testing
4. **Commit** your changes: `git commit -m 'Add amazing feature'`
5. **Push** to the branch: `git push origin feature/amazing-feature`
6. **Open** a Pull Request

### **Contribution Guidelines**
- Follow TypeScript and Python coding standards
- Add tests for new features
- Update documentation as needed
- Ensure no API keys are committed
- Follow conventional commit messages

## 📝 API Documentation

### **Authentication Endpoints**
```http
POST /auth/register        # User registration
POST /auth/login          # User login
POST /auth/verify-otp     # OTP verification
POST /auth/logout         # User logout
```

### **Cryptocurrency Endpoints**
```http
GET  /crypto/prices       # Get current prices
GET  /crypto/history      # Get historical data
GET  /crypto/predict      # Get AI predictions
GET  /crypto/signals      # Get trading signals
```

### **AI & Analytics Endpoints**
```http
POST /ai/chat            # AI chat assistant
GET  /ai/sentiment       # Market sentiment
GET  /ai/forecast        # Price forecasting
GET  /ai/analysis        # Technical analysis
```

## 🔧 Troubleshooting

### **Common Issues**

**Port Already in Use**
```bash
# Kill process using port 3000 or 8000
npx kill-port 3000
npx kill-port 8000
```

**Module Not Found**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# For Python modules
pip install -r requirements.txt --force-reinstall
```

**API Key Issues**
- Verify API keys are correctly set in `.env`
- Check API key validity and rate limits
- Ensure no trailing spaces in environment variables

## 📞 Support & Contact

- **Developer**: Siddhesh Shinde
- **GitHub**: [@Siddhesh-Codes](https://github.com/Siddhesh-Codes)
- **Repository**: [ai-crypto-analytics](https://github.com/Siddhesh-Codes/ai-crypto-analytics)
- **Issues**: [GitHub Issues](https://github.com/Siddhesh-Codes/ai-crypto-analytics/issues)

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CoinMarketCap** for cryptocurrency data
- **Groq** for AI language model capabilities
- **React & FastAPI** communities for excellent documentation
- **Open Source Contributors** for various libraries used

---

<div align="center">

**🚀 Built with ❤️ for the Future of Crypto Analytics**

*A Final Year Project showcasing modern web development, AI/ML integration, and financial technology*

[![GitHub stars](https://img.shields.io/github/stars/Siddhesh-Codes/ai-crypto-analytics?style=social)](https://github.com/Siddhesh-Codes/ai-crypto-analytics/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Siddhesh-Codes/ai-crypto-analytics?style=social)](https://github.com/Siddhesh-Codes/ai-crypto-analytics/network)

</div>