# 🔒 Security Policy

## ⚠️ Never Commit Sensitive Data

This project uses API keys and secrets that must **NEVER** be committed to version control.

### Protected Files (Already in .gitignore)

- ✅ `.env` files (backend, frontend, llm-model)
- ✅ Database files (`*.db`, `*.sqlite`)
- ✅ Virtual environments (`venv/`, `env/`)
- ✅ Node modules (`node_modules/`)
- ✅ API key files (`*key*.txt`, `secrets.json`)
- ✅ Large model files (`*.joblib`, `*.pkl`)

### Required Environment Variables

#### Backend (`backend/.env`)
```env
GROQ_API_KEY=your_groq_api_key
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key
NEWS_API_KEY=your_news_api_key
JWT_SECRET_KEY=generate_random_string
SECRET_KEY=generate_random_string
```

**⚠️ See `backend/.env.example` for the template**

#### Frontend (`frontend/.env`)
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

**⚠️ See `frontend/.env.example` for the template**

## 🔑 Getting API Keys

### Groq API (AI Chat)
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Generate API key
4. Free tier: 14,400 requests/day

### CoinMarketCap API (Crypto Data)
1. Visit [coinmarketcap.com/api](https://coinmarketcap.com/api/)
2. Sign up for free account
3. Get API key from dashboard
4. Free tier: 10,000 calls/month

### NewsAPI (Optional)
1. Visit [newsapi.org](https://newsapi.org/)
2. Sign up for free account
3. Get API key
4. Free tier: 1,000 requests/day

## 🛡️ Security Best Practices

### For Contributors
1. **Never** commit `.env` files
2. **Never** hardcode API keys in source code
3. **Always** use environment variables
4. **Always** check `git status` before committing
5. **Always** review `.gitignore` before adding new secrets

### Generating Secure Keys

```python
# For JWT_SECRET_KEY and SECRET_KEY
import secrets
print(secrets.token_urlsafe(64))
```

```bash
# Or use this command
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## 🚨 If You Accidentally Commit Secrets

If you accidentally commit API keys or secrets:

1. **Immediately rotate/regenerate** all exposed keys
2. **Remove** from git history:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch backend/.env" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (⚠️ only if you own the repo):
   ```bash
   git push origin --force --all
   ```

## 📧 Reporting Security Issues

If you discover a security vulnerability, please email:
**siddhesh.codes21@gmail.com**

**Do NOT** open a public GitHub issue for security vulnerabilities.

## ✅ Pre-Commit Checklist

Before every commit, verify:

- [ ] No `.env` files in staged changes
- [ ] No API keys in source code
- [ ] No database files being committed
- [ ] No large model files (use Git LFS if needed)
- [ ] `.gitignore` is up to date
- [ ] Environment variables use examples (`.env.example`)

### Quick Check Command
```bash
git status --ignored
# Verify .env files are in "Ignored files" section
```

## 🔐 Production Deployment Security

### Environment Variables Setup

**Never** use development keys in production!

1. Generate new API keys for production
2. Use strong, random secret keys
3. Enable HTTPS/SSL
4. Set `DEBUG=false`
5. Configure proper CORS origins
6. Use environment variable management (Railway, Vercel, etc.)

### Recommended .env for Production
```env
DEBUG=false
FRONTEND_URL=https://your-domain.com
BACKEND_URL=https://api.your-domain.com
```

---

**🛡️ Security is everyone's responsibility. Stay vigilant!**
