# AI-Powered Crypto Analytics Agent

[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=flat&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9.5-3178C6?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E?style=flat&logo=scikit-learn)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade full-stack cryptocurrency analytics platform featuring conversational AI insights, real-time market data pipelines, Random Forest machine learning price forecasting, and comprehensive technical indicator analysis.

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Directory Structure](#project-directory-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Installation](#local-installation)
  - [Environment Configuration](#environment-configuration)
  - [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Production Cloud Deployment](#production-cloud-deployment)
  - [Backend Deployment (Render)](#backend-deployment-render)
  - [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
- [Security & Data Protection](#security--data-protection)
- [License](#license)

---

## Executive Summary

The AI-Powered Crypto Analytics Agent is built to provide high-throughput market intelligence, automated trading signal evaluation, and predictive forecasting for cryptocurrency markets. It integrates real-time exchange pricing with LLaMA-based natural language intelligence (via Groq Cloud API) and custom scikit-learn models trained on historical sequence metrics and technical indicators.

The application adheres to clean architecture principles with complete decoupling between the async FastAPI backend and the state-managed React/TypeScript SPA frontend.

---

## System Architecture

```
+-------------------------------------------------------------------------+
|                               Client Layer                              |
|   React 18 SPA + TypeScript + Zustand + Tailwind CSS + Lucide Icons    |
+------------------------------------+------------------------------------+
                                     |
                             REST / WebSockets
                                     |
+------------------------------------+------------------------------------+
|                             API Gateway                                 |
|                  FastAPI + Uvicorn + CORS Middleware                    |
+---------+--------------------------+--------------------------+---------+
          |                          |                          |
+---------v--------+       +---------v--------+       +---------v--------+
|  AI Chat Engine  |       | ML Predictor     |       | Market Data Hub  |
|  Groq LLaMA 3.1  |       | Random Forest R² |       | CoinMarketCap    |
+------------------+       +------------------+       +------------------+
          |                          |                          |
+---------v--------------------------v--------------------------v---------+
|                              Data Layer                                 |
|                    SQLAlchemy ORM + SQLite Storage                      |
+-------------------------------------------------------------------------+
```

---

## Key Features

### Conversational AI & Natural Language Processing
- **LLaMA-3.1 Powered Assistant**: High-speed contextual cryptocurrency chat built on the Groq inference engine.
- **Context-Aware Insights**: Automatically injects portfolio metrics and live market rates into conversation prompts.
- **Sentiment Analysis**: TextBlob NLP scoring for news and market commentary.

### Machine Learning & Quantitative Analytics
- **Price Prediction Model**: Production-ready Random Forest Regressor achieving up to 72% R^2 accuracy.
- **Feature Engineering Pipeline**: Calculates 9 technical metrics including RSI, MACD, Bollinger Bands, Simple/Exponential Moving Averages, and ATR.
- **Cross-Validation**: 5-fold cross-validation pipeline ensuring robustness against overfitting.

### Real-Time Market Data Pipeline
- **Live Rate Integration**: Seamless market feeds for top 48 cryptocurrencies via CoinMarketCap and CoinGecko APIs.
- **Interactive Technical Charts**: High-performance visualizations using Chart.js and Recharts.
- **Automated Price Alerts**: Threshold and percentage-change notification monitors.

### Authentication & User Management
- **Secure Authentication**: JWT (JSON Web Tokens) with HS256 signature verification.
- **Password Security**: Passlib with bcrypt password hashing.
- **Multi-Factor OTP**: Email/SMS verification flow with rate limiting.

---

## Technology Stack

### Frontend Architecture

| Technology | Version | Purpose |
| :--- | :--- | :--- |
| **React** | 18.2.0 | Core UI Library |
| **TypeScript** | 4.9.5 | Type Safety & Interfaces |
| **Tailwind CSS** | 3.3.2 | Utility-First Responsive Styling |
| **Lucide React** | 0.244.0 | UI Icon System |
| **Zustand** | 4.3.7 | Centralized Application State Management |
| **Chart.js** | 4.3.0 | Technical Chart Visualizations |
| **Recharts** | 2.6.2 | Data & Analytics Visualization |
| **Framer Motion** | 10.12.16 | Micro-animations and Transitions |
| **React Router** | 6.10.0 | Client-Side SPA Routing |

### Backend Infrastructure

| Technology | Version | Purpose |
| :--- | :--- | :--- |
| **FastAPI** | 0.104.1 | Asynchronous ASGI Web Framework |
| **Uvicorn** | 0.24.0 | ASGI Server Implementation |
| **SQLAlchemy** | 2.0.23 | Python SQL Toolkit and ORM |
| **Python-JOSE** | 3.3.0 | JWT Token Generation and Decoding |
| **Passlib** | 1.7.4 | Password Hashing (Bcrypt) |
| **Pydantic** | 2.5.0 | Data Validation and Settings Management |

### Machine Learning & Data Science

| Technology | Version | Purpose |
| :--- | :--- | :--- |
| **scikit-learn** | 1.3+ | Random Forest & Predictive Pipelines |
| **NumPy** | 1.24+ | Multi-dimensional Array Computations |
| **Pandas** | 2.0+ | Data Manipulation & Time Series |
| **Groq SDK** | 0.4.1 | Fast LLaMA Model Inference |
| **TextBlob** | 0.17.1 | Lexicon-Based Sentiment Analysis |

---

## Project Directory Structure

```
AI-Powered-Crypto-Analytics-Agent/
├── backend/
│   ├── app/                    # Modular FastAPI controllers & services
│   ├── auth_database.py        # Authentication & User ORM management
│   ├── database.py             # Database engine & connection session
│   ├── models.py               # Database schemas
│   ├── Procfile                # Production runner manifest for cloud PaaS
│   ├── requirements.txt        # Python backend dependencies
│   ├── simple_backend.py       # Primary API service entry point
│   ├── technical_indicators.py # Technical indicator calculations
│   └── websocket_manager.py    # WebSocket connection pool manager
├── frontend/
│   ├── public/                 # Static assets & index.html
│   ├── src/
│   │   ├── components/         # Reusable React components & UI widgets
│   │   ├── config/             # Dynamic API & environment configurations
│   │   ├── contexts/           # React Context providers (Auth)
│   │   ├── pages/              # Application views (Dashboard, Analytics, Portfolio)
│   │   ├── services/          # REST API integration clients
│   │   └── store/              # Zustand global state stores
│   ├── package.json            # Frontend scripts & dependencies
│   ├── tsconfig.json           # TypeScript configuration
│   └── vercel.json             # Vercel SPA routing configuration
├── llm-model/                  # Offline model training & experimental scripts
├── render.yaml                 # Infrastructure-as-Code Blueprint for Render
├── README.md                   # System documentation
└── .gitignore                  # Git repository exclusion manifest
```

---

## Getting Started

### Prerequisites

Ensure you have the following installed on your machine:
- **Node.js**: `v16.14.0` or higher
- **npm**: `v8.0.0` or higher
- **Python**: `3.10` or higher

### Local Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/crypto-analytics-agent.git
   cd crypto-analytics-agent
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Frontend Setup**:
   ```bash
   cd ../frontend
   npm install
   ```

---

### Environment Configuration

Create `.env` files in both the `backend/` and `frontend/` directories (these files are ignored by git to protect credentials).

#### `backend/.env`
```ini
# API Keys (Obtain from respective provider consoles)
GROQ_API_KEY=gsk_your_groq_api_key_here
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key_here
NEWS_API_KEY=your_news_api_key_here

# Security Settings
JWT_SECRET_KEY=your_secure_random_jwt_secret_key
SECRET_KEY=your_secure_random_app_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database Configuration
DATABASE_URL=sqlite:///./crypto_analytics.db
```

#### `frontend/.env`
```ini
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

---

### Running the Application

1. **Start the Backend Service**:
   ```bash
   cd backend
   python simple_backend.py
   ```
   *The backend will start at `http://localhost:8000` (API documentation available at `http://localhost:8000/docs`).*

2. **Start the Frontend Development Server**:
   ```bash
   cd frontend
   npm start
   ```
   *The application will open automatically at `http://localhost:3000`.*

---

## API Documentation

FastAPI automatically generates interactive OpenAPI/Swagger documentation. Once the backend is running, navigate to:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/ai/chat` | Process conversational AI query with Groq LLaMA | No |
| `GET` | `/api/market/search` | Search cryptocurrency assets by symbol/name | No |
| `POST` | `/api/market/price-history` | Fetch historical OHLC price sequences | No |
| `GET` | `/api/technical/indicators/{symbol}` | Get RSI, MACD, Bollinger Bands for asset | No |
| `POST` | `/api/auth/register` | Register new user account | No |
| `POST` | `/api/auth/login` | Authenticate user & return JWT token | No |
| `GET` | `/api/portfolio/assets` | Get user portfolio holdings | Yes |
| `POST` | `/api/alerts` | Set custom price threshold alert | Yes |

---

## Production Cloud Deployment

### Backend Deployment (Render)

1. Sign in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** > **Web Service** and connect your repository.
3. Set the following fields:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn simple_backend:app --host 0.0.0.0 --port $PORT`
4. Configure Environment Variables:
   - `GROQ_API_KEY`: Your Groq Cloud API key
   - `COINMARKETCAP_API_KEY`: Your CoinMarketCap API key
   - `JWT_SECRET_KEY`: Production secret key
   - `SECRET_KEY`: Production secret key
5. Deploy and obtain your backend URL (e.g., `https://crypto-analytics-backend.onrender.com`).

### Frontend Deployment (Vercel)

1. Sign in to [Vercel](https://vercel.com).
2. Click **Add New...** > **Project** and import your repository.
3. Set the following fields:
   - **Framework Preset**: `Create React App`
   - **Root Directory**: `frontend`
4. Add Environment Variable:
   - `REACT_APP_API_URL` = `https://crypto-analytics-backend.onrender.com`
5. Click **Deploy**. Vercel will generate your live production URL.

---

## Security & Data Protection

- **No Hardcoded Credentials**: Secrets are strictly injected via runtime environment variables.
- **Git Protection**: `.env`, database storage files (`*.db`), `.coverage`, and dependency folders are excluded via `.gitignore`.
- **CORS Policies**: Explicit cross-origin request policies implemented via FastAPI middleware.
- **Transport & Storage**: Passwords hashed with salted bcrypt algorithms; API tokens verified statelessly using JWT claims.

---

## License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.