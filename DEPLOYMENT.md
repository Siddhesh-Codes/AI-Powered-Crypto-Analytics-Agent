# Deployment Guide for AI-Powered Crypto Analytics Agent

This guide covers deployment options for free hosting platforms.

## Frontend Deployment (Vercel/Netlify)

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Build the frontend**
   ```bash
   cd frontend
   npm run build
   ```

3. **Deploy to Vercel**
   ```bash
   vercel --prod
   ```

4. **Environment Variables on Vercel**
   - Go to your Vercel dashboard
   - Navigate to your project settings
   - Add environment variables:
     - `REACT_APP_API_URL`: Your backend API URL
     - `REACT_APP_ENVIRONMENT`: production

### Netlify Deployment

1. **Build the frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy to Netlify**
   - Connect your GitHub repository to Netlify
   - Set build command: `cd frontend && npm run build`
   - Set publish directory: `frontend/build`

3. **Environment Variables on Netlify**
   - Go to Site settings > Environment variables
   - Add the same variables as Vercel

## Backend Deployment (Railway/Render/Heroku)

### Railway Deployment

1. **Create railway.toml**
   ```toml
   [build]
   builder = "NIXPACKS"
   
   [deploy]
   startCommand = "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
   
   [env]
   PYTHONPATH = "/app/backend"
   ```

2. **Connect to Railway**
   - Connect your GitHub repository to Railway
   - Set root directory to `/backend`
   - Add environment variables in Railway dashboard

### Render Deployment

1. **Create render.yaml**
   ```yaml
   services:
     - type: web
       name: crypto-analytics-api
       env: python
       buildCommand: "cd backend && pip install -r requirements.txt"
       startCommand: "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
       envVars:
         - key: PYTHON_VERSION
           value: 3.9.16
   ```

### Heroku Deployment

1. **Create Procfile**
   ```
   web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. **Create runtime.txt**
   ```
   python-3.9.16
   ```

3. **Deploy**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## Database Deployment

### PostgreSQL on Railway

1. **Add PostgreSQL Plugin**
   - Go to your Railway project
   - Add PostgreSQL plugin
   - Copy connection details to environment variables

### PostgreSQL on Render

1. **Create PostgreSQL Database**
   - Go to Render dashboard
   - Create new PostgreSQL database
   - Copy connection string to environment variables

### PostgreSQL on Heroku

1. **Add Heroku Postgres Add-on**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

## Environment Variables for Production

### Frontend (.env.production)
```
REACT_APP_API_URL=https://your-backend-api.herokuapp.com
REACT_APP_ENVIRONMENT=production
```

### Backend (.env.production)
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://redis-host:6379/0
SECRET_KEY=your-production-secret-key
COINMARKETCAP_API_KEY=your-real-api-key
NEWS_API_KEY=your-real-api-key
ENVIRONMENT=production
BACKEND_CORS_ORIGINS=https://your-frontend.vercel.app
```

## Free Tier Limitations & Optimizations

### API Rate Limits
- CoinMarketCap Free: 333 calls/day
- NewsAPI Free: 1000 requests/day

### Optimization Strategies
1. **Aggressive Caching**: Cache API responses for 5-10 minutes
2. **Data Prioritization**: Focus on top 50 cryptocurrencies
3. **Batch Requests**: Combine multiple symbol requests
4. **Background Jobs**: Use scheduled tasks for data updates

### Free Hosting Limits
- **Vercel**: 100GB bandwidth/month
- **Netlify**: 100GB bandwidth/month
- **Railway**: 500 hours/month
- **Render**: 750 hours/month

## Monitoring & Analytics

### Free Monitoring Options
1. **Vercel Analytics**: Built-in analytics
2. **Google Analytics**: Web analytics
3. **Sentry**: Error tracking (free tier)
4. **LogRocket**: Session replay (free tier)

## Scaling Considerations

### When to Upgrade
1. Exceeding free tier limits
2. Need for real-time data
3. Advanced analytics requirements
4. Higher accuracy AI models

### Upgrade Path
1. **Paid APIs**: CoinMarketCap Pro, Alpha Vantage
2. **Dedicated Hosting**: DigitalOcean, AWS, Google Cloud
3. **Advanced Database**: Managed PostgreSQL
4. **CDN**: Cloudflare Pro

## Security Best Practices

1. **Environment Variables**: Never commit API keys
2. **CORS**: Configure proper CORS origins
3. **Rate Limiting**: Implement API rate limiting
4. **Input Validation**: Validate all user inputs
5. **HTTPS**: Use HTTPS in production

## Backup Strategy

1. **Database Backups**: Regular PostgreSQL backups
2. **Code Backups**: Git repository with multiple remotes
3. **Model Backups**: Store trained models in cloud storage

## Troubleshooting Common Issues

### Build Failures
1. Check Node.js/Python versions
2. Verify all dependencies are installed
3. Check environment variables

### API Errors
1. Verify API keys are correct
2. Check API rate limits
3. Implement fallback data

### Performance Issues
1. Optimize database queries
2. Implement proper caching
3. Use CDN for static assets
