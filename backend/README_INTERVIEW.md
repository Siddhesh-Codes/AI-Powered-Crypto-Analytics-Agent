# Backend Detailed Interview Overview

## 1) Backend purpose and responsibility

This backend is a FastAPI service acting as:

- API gateway for frontend features (auth, market, portfolio, alerts, news, AI chat)
- integration layer for external providers (CoinGecko, NewsAPI, optionally Groq)
- real-time streaming server via WebSocket subscriptions
- data shaping and resilience layer (caching, fallbacks, response cleanup)

## 2) Architecture breakdown

```text
Frontend (React)
  -> FastAPI app (simple_backend.py)
    -> Auth module (auth_database.py)
    -> News + sentiment module (news_sentiment.py)
    -> Technical indicators module (technical_indicators.py)
    -> WebSocket manager (websocket_manager.py)
    -> External services:
       - CoinGecko (price/market/market chart)
       - NewsAPI / CryptoCompare (news)
       - Groq (AI chat, when configured)

Storage model in current codebase:
- Auth/session persistence: SQLite in auth_database.py
- SQLAlchemy config: PostgreSQL primary + SQLite fallback in database.py
```

## 3) Main modules and what each does

### `simple_backend.py`

- main FastAPI entry point
- contains route definitions for auth, chat, market, portfolio, alerts, signals, news, websocket endpoint
- includes compatibility endpoints so multiple frontend variants can call chat (`/api/v1/ai/chat`, `/api/ai/chat`, `/api/chat`)

### `auth_database.py`

- user registration/login/session operations
- bcrypt password hashing
- JWT generation and validation
- session cleanup functions for expired sessions

### `news_sentiment.py`

- fetches crypto news
- article-level processing
- sentiment scoring (label, polarity, confidence)
- crypto mention extraction and relevance scoring
- mock fallback if API keys/services are unavailable

### `technical_indicators.py`

- indicator calculations (RSI, MACD, Bollinger Bands, moving averages, stochastic, ATR, Williams %R)
- fetches historical market data from CoinGecko and computes trading-oriented signals

### `websocket_manager.py`

- accepts and tracks active WebSocket clients
- supports subscription types (prices, news, indicators, alerts)
- launches per-topic async background loops
- caches price data and broadcasts updates
- cleans up orphaned tasks when clients unsubscribe/disconnect

## 4) API lifecycle and endpoint groups

### A) Authentication endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /verify-token`
- `GET /api/auth/me`

Request lifecycle:

1. Validate incoming payload.
2. Lookup/create user in auth store.
3. On success, return token/user object.
4. Protected endpoints validate bearer token and attach current user context.

### B) AI chat endpoints

- `POST /api/v1/ai/chat` (main)
- `POST /api/ai/chat` and `POST /api/chat` (aliases)
- `GET /api/v1/ai/chat/health`

Request lifecycle:

1. Receive message + user context from frontend.
2. Try real AI provider if configured.
3. If AI fails/unavailable, switch to enhanced fallback response builder.
4. Final response passes markdown cleanup before returning in many flows.

### C) Market and analytics endpoints

- `GET /api/market/data`
- `POST /api/market/price-history`
- `GET /api/market/search`
- `GET /api/market/sentiment`
- `GET /api/technical/indicators/{symbol}`
- `GET /api/trading/signals`

Usage:

- drives dashboard metrics, chart history, search, indicators, and trading signal cards.

### D) Portfolio and alerts endpoints

- `POST /api/portfolio/assets`
- `GET /api/portfolio/assets`
- `PUT /api/portfolio/assets/{asset_id}`
- `DELETE /api/portfolio/assets/{asset_id}`
- `POST /api/portfolio/refresh-prices`
- `POST /api/alerts`
- `GET /api/alerts`
- `DELETE /api/alerts/{alert_id}`

Legacy/extra alert routes also exist in the same backend for alternate flows:

- `POST /api/alerts/create`
- `GET /api/alerts/{user_id}`

### E) News endpoints

- `GET /api/news`
- `GET /api/news/sentiment/{coin}`
- `GET /api/market-sentiment`

Usage:

- article feed, coin-specific sentiment, and aggregate market sentiment.

### F) WebSocket endpoint

- `WS /ws/{client_id}`

Supported message types include subscribe/unsubscribe/ping/get_current_prices, with broadcast updates for subscribed topics.

## 5) Data cleaning, transformation, and enrichment

Yes, backend performs multiple processing stages.

### 1. Price normalization and mapping

- Converts symbols to CoinGecko IDs before querying external API.
- Shapes raw provider payload into frontend-friendly response objects.

### 2. Caching and deduplication behavior

- In-memory caches are used for live prices and some history paths.
- Cache reduces provider calls and improves response latency.

### 3. News enrichment pipeline

- Processes each article into:
  - normalized article schema
  - sentiment label/polarity/confidence
  - mentioned crypto list
  - relevance score

### 4. AI output cleanup

- Markdown-cleaning utility strips formatting artifacts to keep responses readable in chat UI.

### 5. Fallback path handling

- If external dependency fails:
  - chat falls back to deterministic enhanced response mode
  - news may return mock/fallback articles
  - market-related endpoints can return synthetic/mock data in some handlers

## 6) Security and reliability points

### Security controls in code

- bcrypt for password hashing
- JWT for authentication
- bearer-token protected endpoints for user-specific actions
- session expiration and cleanup support

### Reliability patterns

- multiple endpoint aliases for compatibility
- fallback-first strategy for third-party instability
- background websocket loops with cleanup logic
- SQLite fallback behavior in database configuration paths

## 7) Real vs simulated behavior (important to state clearly)

- Real integrations:
  - CoinGecko data fetches
  - NewsAPI when key is present
  - optional Groq AI
  - websocket stream infra
- Simulated/fallback behavior:
  - some market/signal/history routes use random/mock payload generation
  - AI and news fallback content when provider is unavailable

## 8) Interview-ready summary (backend)

"Our backend is designed as a resilient integration service: FastAPI route layer, dedicated auth/news/indicator/websocket modules, and external provider connectors. It standardizes response shapes for frontend consumption, enriches raw data with sentiment and indicators, secures user operations with JWT+bcrypt, and remains available through cache and fallback strategies even when third-party APIs fail."
