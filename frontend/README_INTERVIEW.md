# Frontend Detailed Interview Overview

## 1) Frontend purpose and responsibility

This frontend is a React + TypeScript client that provides one unified dashboard for:

- market discovery (top cryptos, sentiment, indicators)
- portfolio tracking and price refresh
- AI-assisted crypto Q&A
- alerts and trading signals
- news + sentiment visualization

The frontend is not only a UI layer; it also performs business-side shaping of API payloads (mapping, defaults, heuristics, and fallback behavior).

## 2) High-level architecture (what interviewer should understand)

```text
Pages/Components
  -> Zustand Stores (state + async actions)
    -> Service Layer (fetch wrappers + adapters)
      -> Backend APIs (FastAPI on localhost:8000)
      -> External providers (CoinGecko, CryptoCompare, NewsAPI)

Optional real-time channel:
RealTimeData component
  -> WebSocket ws://localhost:8001/ws/{client_id}
```

### Core layers

1. Presentation layer:

- Pages in `src/pages` and components in `src/components`.

2. State layer (Zustand):

- `marketStore`, `portfolioStore`, `alertsStore`, `newsStore`, `tradingSignalsStore`, `authStore`.

3. Data layer (services):

- `cryptoAPI.ts`, `enhancedCryptoAPI.ts`, `newsAPI.ts`, `simpleNewsAPI.ts`.

## 3) Module-by-module overview

### Auth flow

- On app load, frontend checks token via `POST /verify-token`.
- Login/register calls:
  - `POST /api/auth/login`
  - `POST /api/auth/register`
- Token is persisted in localStorage and used in protected endpoints (alerts/portfolio).

### Market flow

- Top market view primarily uses CoinGecko via `enhancedCryptoAPI.fetchRealTimePrices()`.
- Global metrics and deeper analytics use backend APIs through `cryptoAPI`.
- Charts and cards consume normalized `MarketData` objects regardless of source.

### AI Chat flow

- Chat component first checks backend health and finds active port.
- Sends user prompt + short conversation history + user context to `POST /api/chat`.
- If backend is unavailable, component switches to enhanced local fallback response generation.

### Portfolio flow

- Add/update/delete asset operations call backend portfolio endpoints.
- If backend is down, frontend falls back to local persisted state.
- Totals (value, P/L absolute and percent) are derived in store logic.

### Alerts flow

- Create/list/delete calls backend alert endpoints.
- Toggle behavior is local-state based (explicit backend toggle endpoint is not present).
- Alert conditions are checked against market data snapshots in the store.

### News and sentiment flow

- Primary route: `GET /api/news` via `newsStore`.
- Additional direct external fetch exists in `NewsAndSentiment` from CryptoCompare.
- UI shows sentiment tags, category, relevance, and source.

### Trading signals flow

- Fetches `GET /api/trading/signals`.
- If unavailable, uses deterministic mock signals for continuity.

## 4) API map: how each response is used

### Authentication endpoints

- `POST /api/auth/login`, `POST /api/auth/register`, `POST /verify-token`
- Consumed by auth context/store, then propagated to route guards and user profile UI.

### Market endpoints

- `GET /api/market/data`: dashboard totals and dominance cards.
- `GET /api/market/search`: search autosuggest and coin picker.
- `POST /api/market/price-history`: chart series (line/candlestick-like display adapters).
- `GET /api/technical/indicators/{symbol}`: indicator widgets.
- `GET /api/market/sentiment`: sentiment panel.

### Portfolio endpoints

- `POST /api/portfolio/assets`, `GET /api/portfolio/assets`, `POST /api/portfolio/refresh-prices`
- Used to maintain holdings table and recompute portfolio summary.

### Alerts endpoints

- `POST /api/alerts`, `GET /api/alerts`, `DELETE /api/alerts/{id}`
- Used to create, render, and remove user alerts in alerts manager.

### News and signal endpoints

- `GET /api/news`
- `GET /api/trading/signals?timeframe=...&limit=...`
- Used in dedicated cards/pages for news feed and trading decisions.

## 5) Data cleaning and transformation done in frontend

Yes, the frontend does meaningful processing before rendering.

### 1. Data normalization

- CoinGecko/external payloads are mapped to consistent internal interfaces (`MarketData`, `GlobalMetrics`, etc.).
- Symbols are standardized to uppercase for UI consistency.

### 2. Null/undefined safety

- Missing fields are defaulted to safe values (`0`, empty arrays, null guards).
- Prevents chart or card crashes on incomplete API responses.

### 3. Synthetic time-series generation

- `marketStore` can generate local timeframe-aware history (1h, 24h, 7d, 30d, 1y).
- This is used when backend history is not preferred/available in specific paths.

### 4. Sentiment and category enrichment

- News content gets rule-based sentiment labeling (bullish/bearish/neutral),
- coin mention extraction,
- and article category assignment (market/regulation/technology/adoption/trading).

### 5. Fallback and resilience logic

- If primary API fails, the stores/services fall back to alternate API or mock payloads.
- This keeps the interface interactive during outages or rate-limit events.

## 6) Real vs mock behavior (be transparent in interview)

- Real/live paths:
  - CoinGecko market calls
  - backend API calls for auth/portfolio/alerts/news/signals
  - optional WebSocket streaming
- Mock/simulated paths:
  - some chart history generation
  - fallback sentiment/signals/news when endpoints fail
  - local fallback in AI chat when backend unavailable

## 7) Interview-ready summary (frontend)

"Our frontend follows a layered pattern: components -> Zustand stores -> service adapters -> backend/external APIs. We normalize all incoming data to internal interfaces, apply null-safe defaults, and use fallback pipelines to handle API failures gracefully. For user experience, we support both polling/API-based data and optional WebSocket real-time updates."
