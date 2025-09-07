# Development Guide

## Quick Start

### 1. Environment Setup (IMPORTANT!)
```bash
# Copy the example environment file
cd backend
cp .env.example .env

# Edit .env and add your actual API keys:
# - Get Groq API key from: https://console.groq.com/keys
# - Get Gmail App Password from: https://myaccount.google.com/apppasswords
```

### 2. Start Backend
```bash
# Option 1: Use the batch file
start-backend.bat

# Option 2: Manual start
cd backend
python simple_backend.py
```

### 2. Start Frontend
```bash
# Option 1: Use the batch file
start-frontend.bat

# Option 2: Manual start
cd frontend
npm start
```

## Environment Setup

### Backend Environment (.env in backend folder)
```env
# Required for AI Chat
GROQ_API_KEY=your_groq_api_key_here

# Required for OTP Email
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Getting API Keys

1. **Groq API Key**: Sign up at https://groq.com and get your free API key
2. **Gmail App Password**: Enable 2FA on Gmail, then generate an app password

## Project Structure

- `backend/simple_backend.py` - Main API server
- `frontend/src/` - React application source code
- `ai-models/` - ML model implementations
- `start-backend.bat` - Quick backend startup
- `start-frontend.bat` - Quick frontend startup

## Debugging

### Backend Issues
- Check terminal output when running `python simple_backend.py`
- Verify environment variables in `.env` file
- API docs available at http://localhost:8000/docs

### Frontend Issues  
- Check browser console for errors
- Verify backend is running on port 8000
- Check network tab for failed API calls

## Common Commands

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install

# Run tests
cd backend
python -m pytest

# Build frontend for production
cd frontend
npm run build
```
