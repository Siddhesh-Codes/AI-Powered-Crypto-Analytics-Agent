# 🚀 AI-Powered Crypto Analytics Application

[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=flat&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9.5-3178C6?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

A full-stack cryptocurrency analytics application with **AI chat capabilities**, **real-time market data**, and **technical analysis**. Built as a Final Year Project showcasing modern web development and AI integration with cryptocurrency markets.

## ✨ Key Features

### 🤖 **AI-Powered Features**
- **AI Chat Assistant**: Powered by Groq API for cryptocurrency market insights and Q&A
- **Technical Analysis**: RSI, MACD, Bollinger Bands, and other technical indicators
- **Price Prediction Models**: LSTM and ARIMA models for forecasting (development stage)
- **Market Sentiment Analysis**: News sentiment analysis capabilities

### 📊 **Market Data & Analytics**
- **Live Price Monitoring**: Real-time cryptocurrency price tracking via CoinMarketCap API
- **Interactive Charts**: Price visualization with Chart.js
- **Technical Indicators**: Advanced technical analysis tools
- **Market Overview**: Global cryptocurrency market metrics

### 🔐 **User Management**
- **Secure Authentication**: JWT-based authentication system
- **User Registration & Login**: Complete user account management
- **Protected Routes**: Secure access to user-specific features

### 📱 **Modern UI/UX**
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Interactive Components**: Modern React components with TypeScript
- **Real-time Updates**: WebSocket integration for live data
- **Professional Interface**: Clean and intuitive user experience

## 🛠️ Technology Stack

### **Frontend Architecture**
- **React 18** with TypeScript for type-safe development
- **Tailwind CSS** for modern, responsive styling
- **Chart.js** for data visualizations
- **React Router** for client-side routing
- **Axios** for API communication
- **React Hot Toast** for notifications

### **Backend Infrastructure**
- **FastAPI** for high-performance API development
- **SQLite** for data persistence
- **WebSocket** for real-time communication
- **JWT** for secure authentication
- **Uvicorn** as ASGI server

### **AI/ML & Data Processing**
- **Groq API** for AI chat capabilities
- **TensorFlow/Keras** for LSTM neural networks (in development)
- **Statsmodels** for ARIMA time series analysis (in development)
- **Custom Technical Indicators** implementation

### **External APIs & Services**
- **CoinMarketCap API** for cryptocurrency data
- **News API** for market news (in development)
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
Use the provided batch scripts for Windows:

```bash
# Start frontend development server
start-frontend.bat

# Start backend API server
start-backend.bat
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

# ️ Database Configuration
DATABASE_URL=sqlite:///./crypto_analytics.db

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
| **NewsAPI** | Market News (Future) | ✅ 1,000 requests/day | [newsapi.org](https://newsapi.org/) |

## �️ Application Usage

### **Development Mode**
```bash
# Start frontend (port 3000)
start-frontend.bat
# OR
cd frontend && npm start

# Start backend (port 8000)
start-backend.bat
# OR
cd backend && python simple_backend.py
```

### **Available Scripts**
| Command | Description |
|---------|-------------|
| `start-frontend.bat` | Start frontend development server |
| `start-backend.bat` | Start backend API server |
| `cd frontend && npm start` | Start frontend manually |
| `cd backend && python simple_backend.py` | Start backend manually |

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
│   ├──  simple_backend.py     # Main application server
│   ├── 📄 auth_database.py      # Authentication system
│   ├── 📄 technical_indicators.py # Trading indicators
│   ├── 📄 news_sentiment.py     # Sentiment analysis
│   ├── 📄 websocket_manager.py  # WebSocket management
│   └── 📄 requirements.txt      # Python dependencies
│
├── 📁 ai-models/                # AI/ML Model Implementations (Development)
│   ├── 📁 lstm/                 # LSTM neural network models
│   │   └── 📄 lstm_predictor.py
│   └── 📁 arima/                # ARIMA time series models
│       └── 📄 arima_predictor.py
│
├── 📄 README.md                 # Project documentation
├── 📄 start-frontend.bat        # Windows batch scripts
└── 📄 start-backend.bat         # for easy development
```

## 🧪 AI/ML Model Training (Development Stage)

The AI/ML models are currently in development and can be found in the `ai-models/` directory:

### **Available Models**
- **LSTM Neural Networks**: For deep learning-based price prediction
- **ARIMA Models**: Statistical time series forecasting
- **Technical Indicators**: RSI, MACD, Bollinger Bands implementation

### **Current Implementation Status**
- ✅ Model structure and classes implemented
- ⚠️ Training pipelines under development
- ⚠️ Integration with main application pending

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

### **Security Features**
- ✅ JWT token-based authentication
- ✅ Password hashing
- ✅ CORS configuration
- ✅ Input validation and sanitization
- ✅ Secure API endpoints

### **API Key Management**
1. **Obtain API keys** from respective providers
2. **Store securely** in `.env` files
3. **Never commit** API keys to version control
4. **Rotate keys** if accidentally exposed
5. **Use environment variables** in production

## 🧪 Testing

### **Current Testing Status**
- ⚠️ Testing framework setup in progress
- ✅ Manual API testing available via `/docs` endpoint
- ✅ Frontend components tested manually

### **Planned Testing**
- **Unit Tests**: Component and function testing
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Full user flow testing

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

## 📊 Current Features

### **Market Data Dashboard**
- Real-time cryptocurrency price tracking
- Market overview and global metrics
- Interactive price charts

### **AI Chat Assistant**
- Natural language crypto market queries
- Powered by Groq API
- Market insights and analysis

### **User Authentication**
- Secure user registration and login
- JWT-based authentication
- Protected user routes

### **Technical Analysis**
- Basic technical indicators
- Price trend analysis
- Market data visualization

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
POST /api/auth/register   # User registration
POST /api/auth/login      # User login
POST /api/auth/logout     # User logout
GET  /api/auth/me         # Get current user
```

### **Cryptocurrency Endpoints**
```http
GET  /api/v1/crypto/global-metrics     # Global market data
GET  /api/v1/crypto/top-cryptos        # Top cryptocurrencies
GET  /api/market/data                  # Market data
```

### **AI & Chat Endpoints**
```http
POST /api/v1/ai/chat     # AI chat assistant
GET  /api/v1/ai/chat/health  # Chat service health
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
# For frontend
cd frontend
del /s node_modules package-lock.json
npm install

# For Python modules
cd backend
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