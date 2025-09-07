# AI-Powered Crypto Analytics Application

A comprehensive full-stack cryptocurrency analytics application with AI-powered forecasting capabilities.

## 🚀 Features

- **Real-time Cryptocurrency Tracking**: Live price monitoring and market analysis
- **AI-Powered Forecasting**: LSTM, ARIMA, and Transformer models for price prediction
- **Technical Analysis**: RSI, MACD, Bollinger Bands indicators
- **Market Sentiment Analysis**: Social media and news sentiment tracking
- **User Authentication**: Secure login with OTP verification
- **Portfolio Management**: Track and analyze your crypto investments
- **AI Chat Assistant**: Get intelligent crypto market insights

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Chart.js** for visualizations
- **Zustand** for state management

### Backend
- **FastAPI** for API server
- **Python** with AI/ML libraries
- **PostgreSQL** for data storage
- **Redis** for caching

### AI/ML
- **TensorFlow/Keras** for LSTM models
- **Statsmodels** for ARIMA analysis
- **Transformers** for advanced modeling
- **NLTK** for sentiment analysis
- **Groq API** for AI chat functionality

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **PostgreSQL** (optional, uses SQLite by default)

### 1. Clone the Repository
```bash
git clone https://github.com/Siddhesh-Codes/ai-crypto-analytics.git
cd ai-crypto-analytics
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env file with your actual API keys and credentials

python simple_backend.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install

# Copy and configure environment variables
cp .env.example .env
# Edit .env file if needed

npm start
```

### 4. Environment Configuration
⚠️ **IMPORTANT**: Never commit your actual API keys!

Create a `.env` file in the backend directory with your actual values:
```env
# Get your Groq API key from: https://groq.com
GROQ_API_KEY=your_actual_groq_api_key_here

# Email configuration for OTP
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
```

## 🔧 Usage

1. **Start the Backend**: Navigate to `/backend` and run `python simple_backend.py`
2. **Start the Frontend**: Navigate to `/frontend` and run `npm start`
3. **Access the Application**: Open `http://localhost:3000` in your browser
4. **API Documentation**: Available at `http://localhost:8000/docs`

## 🔐 Security Notes

- **Never commit `.env` files** - they contain sensitive API keys
- **Always use `.env.example`** for sharing configuration structure
- **Rotate API keys** if accidentally exposed
- **Use strong passwords** for email configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m 'Add feature'`
4. **Ensure no secrets are committed**
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ by Siddhesh Shinde**