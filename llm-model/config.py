"""
Configuration for Crypto Analytics LLM Model Training
"""

import os

# API Keys for data fetching
COINMARKETCAP_API_KEY = "4398999d-b92c-484c-ad6f-a851679a90cd"
NEWSAPI_KEY = "0c37da84674d462a814bf59b7b3763f6"

# Model Configuration
MODEL_NAME = "CryptoAnalytics-LLM-v1.0"
MODEL_TYPE = "Transformer-based Multi-task Learning"
EMBEDDING_DIM = 512
HIDDEN_DIM = 1024
NUM_LAYERS = 12
NUM_HEADS = 8
DROPOUT_RATE = 0.1

# Training Configuration
BATCH_SIZE = 32
LEARNING_RATE = 0.0001
NUM_EPOCHS = 50
VALIDATION_SPLIT = 0.2
EARLY_STOPPING_PATIENCE = 5

# Data Configuration
# TOP 50 CRYPTOCURRENCIES (still just 1 API call!)
CRYPTO_SYMBOLS = [
    "BTC", "ETH", "USDT", "BNB", "XRP", "USDC", "ADA", "SOL", "DOGE", "TRX",
    "DOT", "MATIC", "LTC", "SHIB", "AVAX", "LINK", "UNI", "XLM", "BCH", "ATOM",
    "ETC", "XMR", "APT", "NEAR", "ARB", "OP", "FIL", "ICP", "VET", "ALGO",
    "HBAR", "QNT", "GRT", "SAND", "MANA", "AAVE", "EOS", "FTM", "AXS", "FLOW",
    "XTZ", "THETA", "EGLD", "KCS", "CHZ", "ZEC", "CAKE", "MKR", "RUNE", "ENJ"
]

# NEWS CATEGORIES (5 categories x 20 articles = 100 total, within free limit)
NEWS_CATEGORIES = ["crypto", "blockchain", "bitcoin", "ethereum", "cryptocurrency"]

SEQUENCE_LENGTH = 100
PREDICTION_HORIZON = 7  # days

# API RATE LIMITING (to stay within free tier)
MAX_NEWS_PER_CATEGORY = 20  # Total: 5 x 20 = 100 articles (safe for free tier)

# Paths
DATA_DIR = "data"
MODEL_DIR = "models"
LOGS_DIR = "logs"
PLOTS_DIR = "plots"

# Create directories if they don't exist
for directory in [DATA_DIR, MODEL_DIR, LOGS_DIR, PLOTS_DIR]:
    os.makedirs(directory, exist_ok=True)

print("[SUCCESS] LLM Model Configuration Loaded Successfully!")
