from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
import uvicorn
import os
import asyncio
import random
import smtplib
import secrets
import hashlib
import jwt
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables")

# Create FastAPI instance
app = FastAPI(
    title="Crypto Analytics Agent API",
    description="AI-Powered Cryptocurrency Analytics and Forecasting API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication and Email Configuration
security = HTTPBearer()

# Email Configuration
SMTP_USERNAME = os.getenv("GMAIL_USER", "siddheshshinde358@gmail.com")
SMTP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "ltwy nncf acwz pzpj")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))

# In-memory storage (replace with database in production)
pending_registrations = {}
verified_users = {
    "admin@cryptoanalytics.com": {
        "email": "admin@cryptoanalytics.com",
        "password_hash": "pre_verified_admin",
        "is_verified": True,
        "created_at": datetime.now()
    }
}
otp_storage = {}

# Pydantic models for authentication
class UserRegistration(BaseModel):
    email: str
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserLogin(BaseModel):
    email: str
    password: str

class OTPVerification(BaseModel):
    email: str
    otp: str

class AuthResponse(BaseModel):
    message: str
    success: bool
    token: Optional[str] = None
    user: Optional[Dict[str, Any]] = None

def send_otp_email(email: str, otp: str) -> bool:
    """Send OTP via Gmail SMTP"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_USERNAME
        msg['To'] = email
        msg['Subject'] = "🔐 Your CryptoAnalytics Login Code"
        
        # Create HTML email body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center;">
                        <h1 style="color: white; margin: 0;">🚀 CryptoAnalytics</h1>
                        <p style="color: #cbd5e1; margin: 10px 0 0 0;">AI-Powered Cryptocurrency Platform</p>
                    </div>
                    
                    <div style="background: #f8fafc; padding: 30px; border-radius: 10px; margin-top: 20px; text-align: center;">
                        <h2 style="color: #1e293b; margin-bottom: 20px;">🔐 Your Security Code</h2>
                        <p style="color: #475569;">Your verification code for CryptoAnalytics is:</p>
                        
                        <div style="background: white; border: 2px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 20px 0; font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #1e293b;">
                            {otp}
                        </div>
                        
                        <p style="color: #64748b; font-size: 14px; margin-top: 25px;">
                            ⏰ This code expires in {OTP_EXPIRY_MINUTES} minutes<br>
                            🔒 Never share this code with anyone
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                        
                        <p style="color: #94a3b8; font-size: 12px; text-align: center;">
                            CryptoAnalytics - AI-Powered Cryptocurrency Analytics Platform<br>
                            If you didn't request this code, please ignore this email.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Attach HTML part
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ OTP email sent to {email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send OTP email to {email}: {e}")
        return False

def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return f"{random.randint(100000, 999999):06d}"

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_otp_code(email: str, provided_otp: str) -> bool:
    """Verify OTP code for email"""
    if email not in otp_storage:
        print(f"❌ No OTP found for email: {email}")
        return False
    
    stored_data = otp_storage[email]
    stored_otp = stored_data["otp"]
    expiry_time = stored_data["expiry"]
    
    print(f"🔍 Verifying OTP for {email}")
    print(f"📝 Stored OTP: {stored_otp}, Provided: {provided_otp}")
    print(f"⏰ Expiry: {expiry_time}, Current: {datetime.now()}")
    
    # Check if OTP has expired
    if datetime.now() > expiry_time:
        print(f"⏰ OTP expired for {email}")
        del otp_storage[email]
        return False
    
    # Check if OTP matches
    if stored_otp != provided_otp:
        print(f"❌ OTP mismatch for {email}")
        return False
    
    print(f"✅ OTP verified for {email}")
    return True

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, Any]]] = []
    user_context: Optional[Dict[str, Any]] = {}

class ChatResponse(BaseModel):
    response: str
    source: str
    suggestions: Optional[List[str]] = []
    
# Global variables for AI service
AI_SERVICE_AVAILABLE = False
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Try to import and initialize Groq
try:
    import groq
    if GROQ_API_KEY:
        groq_client = groq.Groq(api_key=GROQ_API_KEY)
        AI_SERVICE_AVAILABLE = True
        print("✅ Groq AI service initialized successfully!")
    else:
        print("⚠️ GROQ_API_KEY not found in environment variables")
except ImportError:
    print("⚠️ Groq library not installed. Install with: pip install groq")
except Exception as e:
    print(f"⚠️ Error initializing Groq: {e}")

async def get_real_ai_response(user_message: str, context: Dict[str, Any] = {}) -> str:
    """Get response from real AI service (Groq)"""
    if not AI_SERVICE_AVAILABLE:
        raise Exception("AI service not available")
    
    try:
        # Create crypto-focused system prompt
        system_prompt = """You are an expert cryptocurrency analyst and trading advisor. 
        You provide intelligent, data-driven insights about crypto markets, trading strategies, 
        portfolio analysis, and blockchain technology. Always give practical, actionable advice 
        while mentioning that this is not financial advice. Be concise but informative.
        Use emojis and markdown formatting to make responses engaging."""
        
        # Add context if available
        context_str = ""
        if context.get("portfolio_value"):
            context_str += f"User's portfolio value: ${context['portfolio_value']:,.2f}\n"
        if context.get("portfolio_change"):
            context_str += f"24h portfolio change: {context['portfolio_change']:.2f}%\n"
        if context.get("top_cryptos"):
            context_str += f"Current top cryptos in portfolio: {[crypto.get('symbol', '') for crypto in context.get('top_cryptos', [])]}\n"
        
        full_prompt = f"{system_prompt}\n\nUser context:\n{context_str}\n\nUser question: {user_message}"
        
        # Call Groq API
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        raise e

async def get_enhanced_fallback_response(user_message: str, context: Dict[str, Any] = {}) -> str:
    """ChatGPT-style intelligent responses for any crypto question"""
    await asyncio.sleep(0.3)  # Simulate AI thinking time
    
    message_lower = user_message.lower()
    timestamp = datetime.now().strftime("%H:%M")
    
    # Comprehensive analysis of user question patterns
    
    # Bitcoin analysis
    if any(word in message_lower for word in ['bitcoin', 'btc']):
        return f"""🟠 **Bitcoin Analysis** • {timestamp}

Bitcoin continues to dominate the cryptocurrency landscape as digital gold. Here's my comprehensive analysis:

**📊 Market Position:**
• **Market Cap**: ~$2.1 trillion (62% crypto dominance)
• **Current Range**: Testing key psychological levels
• **Institutional Flow**: Strong ETF adoption driving demand
• **Network Health**: Hash rate at all-time highs, security robust

**🔮 Technical Outlook:**
• **Support Levels**: Strong accumulation zones around major psychological barriers
• **Resistance**: Previous all-time highs creating selling pressure
• **Volume**: Institutional buying patterns visible in large block trades
• **Trend**: Long-term bullish structure intact despite short-term volatility

**💡 Investment Thesis:**
Bitcoin's fixed supply of 21 million coins, growing institutional adoption, and position as uncorrelated digital asset make it compelling for portfolio allocation. Consider:
- Dollar-cost averaging during volatility
- Long-term holding (4+ years) historically profitable
- Allocation of 5-10% of investment portfolio

**⚠️ Risk Factors:**
Regulatory developments, macroeconomic policy changes, and energy consumption concerns remain key monitoring points.

*This analysis combines technical, fundamental, and sentiment factors for comprehensive insight.*"""

    # Ethereum analysis
    elif any(word in message_lower for word in ['ethereum', 'eth']):
        return f"""⚫ **Ethereum Deep Dive** • {timestamp}

Ethereum remains the world's programmable blockchain, powering the decentralized economy:

**🏗️ Network Fundamentals:**
• **Smart Contracts**: 3,000+ DApps running on mainnet
• **DeFi TVL**: $50+ billion locked in protocols
• **NFT Marketplace**: 90%+ of NFT trading volume
• **Layer 2 Growth**: Polygon, Arbitrum, Optimism scaling rapidly

**⚡ Technical Evolution:**
• **Proof of Stake**: 99.95% energy reduction post-Merge
• **Staking Rewards**: ~4-6% APY for validators
• **Gas Optimization**: EIP-1559 and Layer 2s reducing fees
• **Future Upgrades**: Sharding and further scalability improvements

**📈 Value Propositions:**
1. **Utility Token**: Required for all network operations
2. **Yield Generation**: Staking provides passive income
3. **Deflationary Mechanics**: Fee burning reduces supply
4. **Developer Ecosystem**: Largest blockchain developer community

**💎 Investment Strategy:**
Ethereum benefits from network effects and utility demand. Consider:
- Staking for yield (solo or liquid staking)
- Long-term hold for ecosystem growth
- DCA approach during market volatility

**🎯 Price Catalysts:**
ETF approval potential, institutional staking adoption, Layer 2 mainstream usage, and continued DeFi innovation."""

    # Altcoin analysis  
    elif any(word in message_lower for word in ['solana', 'sol', 'cardano', 'ada', 'polygon', 'matic', 'avalanche', 'avax', 'chainlink', 'link', 'polkadot', 'dot']):
        coin_mentioned = next((word for word in ['solana', 'cardano', 'polygon', 'avalanche', 'chainlink', 'polkadot'] if word in message_lower), 'altcoin')
        
        return f"""🚀 **{coin_mentioned.title()} Analysis** • {timestamp}

**{coin_mentioned.title()} Comprehensive Assessment:**

**🔧 Technology & Use Case:**
{
    "High-performance blockchain optimized for speed and low costs. Powers DeFi, NFTs, and Web3 applications with sub-second finality." if 'solana' in coin_mentioned else
    "Research-driven blockchain with peer-reviewed development. Focus on sustainability, interoperability, and formal verification." if 'cardano' in coin_mentioned else  
    "Ethereum's leading scaling solution with growing ecosystem of dApps and partnerships with major enterprises." if 'polygon' in coin_mentioned else
    "Subnet architecture enabling custom blockchains. Powers enterprise and gaming applications with high throughput." if 'avalanche' in coin_mentioned else
    "Decentralized oracle network connecting blockchains to real-world data. Essential infrastructure for DeFi and smart contracts." if 'chainlink' in coin_mentioned else
    "Interoperability-focused blockchain enabling cross-chain communication. Parachain auction model creates unique economics." if 'polkadot' in coin_mentioned else
    "Strong fundamentals with clear utility and growing adoption."
}

**📊 Market Position:**
• **Ranking**: Top 10 cryptocurrency by market cap
• **Adoption**: Growing developer activity and user base  
• **Partnerships**: Enterprise and institutional collaborations
• **Competition**: Strong differentiation in crowded L1/L2 space

**💰 Investment Considerations:**
**Bullish Factors:**
- Unique technology solving real problems
- Strong development team and community
- Growing ecosystem and usage metrics
- Institutional interest and partnerships

**Risk Factors:**
- High competition in blockchain space
- Technology execution risks
- Regulatory uncertainty for some features
- Market volatility and correlation risks

**🎯 Strategy Recommendation:**
Consider as part of diversified crypto portfolio (10-20% allocation). Dollar-cost average during volatility periods and hold for technology adoption cycles (2-4 years).

*Research the specific project's roadmap, tokenomics, and competitive positioning for deeper analysis.*"""

    # Market analysis
    elif any(word in message_lower for word in ['market', 'trend', 'analysis', 'outlook', 'bull', 'bear', 'cycle']):
        return f"""📊 **Crypto Market Intelligence** • {timestamp}

**🌐 Current Market Landscape:**

The cryptocurrency market is experiencing a fascinating convergence of institutional adoption, technological maturation, and regulatory evolution:

**📈 Bull Market Indicators:**
• **Institutional Adoption**: Bitcoin ETFs crossing $100B in assets
• **Corporate Treasury**: Companies adding crypto to balance sheets
• **Regulatory Clarity**: Clear frameworks emerging globally
• **Technology Maturation**: Layer 2s solving scalability, DeFi growing sophistication

**⚖️ Market Dynamics:**
• **Cycle Stage**: Mid-cycle with room for growth
• **Correlation**: Decreasing correlation with traditional markets
• **Volatility**: High but decreasing as market matures
• **Liquidity**: Improving with institutional participation

**🔮 Macro Factors:**
1. **Federal Reserve Policy**: Interest rates affecting risk appetite
2. **Inflation Hedge**: Crypto viewed as alternative store of value
3. **Geopolitical Tensions**: Driving safe-haven demand
4. **Currency Debasement**: Fiat devaluation supporting crypto thesis

**🎯 Sector Rotation Patterns:**
1. **Bitcoin First**: Store of value narrative leads
2. **Ethereum Second**: Smart contract platform benefits
3. **Altcoin Season**: Speculation flows to smaller caps
4. **DeFi/NFT Cycles**: Utility tokens gain during innovation waves

**💡 Strategic Positioning:**
- **Bear Market Strategy**: Accumulate quality projects, DCA approach
- **Bull Market Strategy**: Take profits systematically, avoid FOMO
- **All Weather**: Diversified portfolio, risk management, long-term perspective

**⚠️ Key Risks to Monitor:**
Regulatory overreach, macroeconomic recession, technology failures, market manipulation, and systemic crypto industry risks.

*Market cycles typically last 3-4 years. Position for long-term while managing short-term volatility.*"""

    # Technical analysis
    elif any(word in message_lower for word in ['technical', 'chart', 'rsi', 'macd', 'support', 'resistance', 'pattern', 'indicator']):
        return f"""📈 **Technical Analysis Masterclass** • {timestamp}

**🔧 Crypto Technical Analysis Framework:**

Technical analysis in crypto requires understanding unique market characteristics while applying proven methodologies:

**📊 Core Indicators for Crypto:**

**RSI (Relative Strength Index):**
• **Crypto Adjustment**: Markets stay overbought/oversold longer than traditional assets
• **Entry Signals**: RSI < 30 (oversold) often good accumulation zones
• **Exit Signals**: RSI > 70 (overbought) consider profit-taking
• **Divergence**: Price vs RSI divergence often precedes reversals

**MACD (Moving Average Convergence Divergence):**
• **Trend Confirmation**: MACD crossovers with volume confirmation
• **Momentum Shifts**: Histogram showing acceleration/deceleration
• **Crypto Adaptation**: Use longer periods (21/50/100) for less noise

**Support & Resistance:**
• **Psychological Levels**: Round numbers ($100K, $50K) extremely significant
• **Previous ATH/ATL**: Former highs become resistance, lows become support
• **Volume Confirmation**: High volume at levels increases significance
• **Fibonacci Retracements**: 0.618, 0.5, 0.382 levels often respected

**📉 Advanced Patterns:**
• **Cup and Handle**: Bullish continuation pattern common in crypto
• **Bull/Bear Flags**: Powerful trend continuation signals
• **Double Top/Bottom**: Major reversal patterns at cycle peaks/troughs
• **Head and Shoulders**: Reliable reversal pattern with volume confirmation

**⏰ Timeframe Strategy:**
• **Scalping**: 1m, 5m charts (high risk, quick profits)
• **Day Trading**: 15m, 1h charts (moderate timeframe)
• **Swing Trading**: 4h, daily charts (recommended for most)
• **Position Trading**: Weekly, monthly charts (long-term trends)

**🎯 Crypto-Specific Considerations:**
1. **24/7 Markets**: Weekend gaps don't exist, continuous trading
2. **High Volatility**: Larger stop losses needed, position sizing critical
3. **News Impact**: Fundamental events override technical patterns
4. **Whale Influence**: Large holders can invalidate technical signals
5. **Exchange Differences**: Price variations across platforms

**💡 Risk Management Rules:**
- Never risk more than 2% per trade
- Always use stop losses
- Take profits systematically
- Don't overtrade or revenge trade
- Keep detailed trading journal

*Technical analysis provides probability, not certainty. Combine with fundamental analysis for best results.*"""

    # DeFi and yield farming
    elif any(word in message_lower for word in ['defi', 'yield', 'farming', 'staking', 'liquidity', 'apy', 'lending', 'protocol']):
        return f"""🏦 **DeFi & Yield Strategy Guide** • {timestamp}

**🌊 Decentralized Finance Landscape:**

DeFi has revolutionized traditional finance, offering permissionless access to sophisticated financial products:

**💰 Yield Generation Strategies:**

**🔒 Staking (Lower Risk):**
• **Ethereum 2.0**: 4-6% APY, liquid staking via Lido/Rocket Pool
• **Cardano**: 4-5% APY, no lockup period, delegated staking
• **Solana**: 6-8% APY, automatic compounding available
• **Cosmos Ecosystem**: 8-15% APY across various chains
• **Polkadot**: 10-12% APY through nomination pools

**🌊 Liquidity Providing (Medium Risk):**
• **Uniswap V3**: 5-50% APY, concentrated liquidity, impermanent loss risk
• **Curve Finance**: 3-20% APY, stable pairs safer, boosted rewards with veCRV
• **Balancer**: 8-25% APY, multiple token pools, auto-rebalancing
• **SushiSwap**: 10-40% APY, cross-chain opportunities

**💎 Lending Protocols (Low-Medium Risk):**
• **Aave**: 2-12% APY, flash loans, collateral efficiency
• **Compound**: 1-8% APY, algorithmic interest rates
• **Maker**: 3-8% APY through DSR, DAI stablecoin
• **Benqi (Avalanche)**: 5-15% APY, native AVAX integration

**🎯 Advanced Strategies:**

**Yield Farming:**
- Provide liquidity → Earn trading fees + token rewards
- Compound yields by reinvesting rewards
- Farm governance tokens for additional upside

**Leverage Yield Farming:**
- Borrow against collateral to increase position size
- Amplifies both returns and risks significantly
- Requires careful monitoring of liquidation ratios

**Delta-Neutral Strategies:**
- Hedge price exposure while capturing yield
- Long spot + short perpetual futures
- Earn funding rates + staking/lending yields

**⚠️ Risk Management Framework:**

**Smart Contract Risk:**
- Use only audited, battle-tested protocols
- Diversify across multiple platforms
- Understand protocol mechanics and governance

**Impermanent Loss:**
- Occurs when token ratios change in liquidity pools
- Higher with volatile pairs vs stablecoin pairs
- Calculate IL before providing liquidity

**Liquidation Risk:**
- Monitor collateral ratios continuously  
- Set conservative ratios (>200%)
- Use price alerts and automatic tools

**💡 Practical Implementation:**
1. **Start Small**: Begin with blue-chip protocols and small amounts
2. **Understand Completely**: Never invest in strategies you don't understand
3. **Gas Considerations**: Factor transaction costs into yield calculations
4. **Tax Implications**: Keep detailed records for DeFi activities
5. **Insurance**: Consider protocol insurance (Nexus Mutual, InsurAce)

**🏆 Recommended Portfolio Allocation:**
- 40% Low-risk staking (ETH, ADA, SOL)
- 30% Medium-risk lending (Aave, Compound)
- 20% Liquidity providing (stable pairs)
- 10% Experimental/high-yield strategies

*DeFi yields are attractive but come with unique risks. Never invest more than you can afford to lose.*"""

    # Trading and investment strategy
    elif any(word in message_lower for word in ['trade', 'trading', 'strategy', 'buy', 'sell', 'when', 'investment', 'portfolio']):
        return f"""💼 **Crypto Trading & Investment Mastery** • {timestamp}

**🎯 Comprehensive Trading Framework:**

**📊 Market Analysis Hierarchy:**
1. **Macro Analysis**: Global economic conditions, regulatory environment
2. **Sector Analysis**: Which crypto sectors are outperforming
3. **Individual Analysis**: Specific project fundamentals and technicals
4. **Timing Analysis**: Entry/exit optimization using multiple indicators

**⚡ Trading Strategies by Timeframe:**

**Scalping (Minutes to Hours):**
• **Advantages**: Quick profits, limited exposure
• **Requirements**: Advanced technical skills, low latency execution
• **Tools**: Order book analysis, level 2 data, automated systems
• **Risk**: High stress, frequent trading costs, prone to overtrading

**Day Trading (Hours to 1 Day):**
• **Focus**: Intraday price movements and momentum
• **Strategy**: Breakout trading, reversal patterns, news catalyst trading
• **Risk Management**: Strict stop losses, position sizing, no overnight holds
• **Success Rate**: Requires discipline and risk management

**Swing Trading (Days to Weeks):**
• **Sweet Spot**: Captures medium-term trends and corrections
• **Analysis**: Daily/4H charts, trend following, momentum indicators
• **Advantages**: Less stressful, higher success rates for retail traders
• **Strategy**: Buy dips in uptrends, sell rallies in downtrends

**Position Trading (Weeks to Years):**
• **Philosophy**: Long-term value creation and technology adoption
• **Research**: Deep fundamental analysis, tokenomics, team evaluation
• **Patience**: Riding through market cycles and volatility
• **Compounding**: Reinvesting gains and staking rewards

**🏆 Portfolio Construction Models:**

**Conservative Crypto Portfolio:**
• 60% Bitcoin (store of value, lowest volatility)
• 25% Ethereum (smart contract platform leader)
• 10% Top 10 altcoins (diversified exposure)
• 5% Stablecoins (opportunistic purchases)

**Growth-Oriented Portfolio:**
• 40% BTC/ETH (foundation)
• 35% Large-cap altcoins (SOL, ADA, DOT, AVAX)
• 20% Mid-cap growth projects (AI, gaming, DeFi)
• 5% Speculative/emerging technologies

**Aggressive High-Risk Portfolio:**
• 25% BTC/ETH (anchor)
• 30% Established altcoins
• 30% Emerging protocols and sectors
• 15% Speculative plays and new launches

**💡 Risk Management Principles:**

**Position Sizing:**
- Never risk more than 1-2% of portfolio per trade
- Kelly Criterion for optimal position sizing
- Scale into positions during volatility

**Stop Loss Strategy:**
- Technical stops (below support levels)
- Percentage stops (10-20% for crypto)
- Time stops (exit after X days if no progress)

**Profit Taking:**
- Scale out systematically (25%, 50%, 75%)
- Lock in profits during parabolic moves
- Leave runners for maximum upside

**🔮 Market Timing Indicators:**

**Bull Market Signals:**
• Institutional adoption increasing
• Mainstream media coverage turning positive
• Long-term holders accumulating
• Technical breakouts with volume

**Bear Market Signals:**
• Regulatory crackdowns and negative news
• Long-term holders distributing
• Technical breakdowns below major support
• Risk-off sentiment in broader markets

**⚠️ Common Trading Mistakes:**
1. **FOMO**: Buying after major rallies
2. **Panic Selling**: Selling after major drops
3. **Overleverage**: Using too much borrowed money
4. **No Plan**: Trading without clear entry/exit rules
5. **Emotional Decisions**: Letting fear/greed drive decisions

**🎯 Success Metrics:**
- Risk-adjusted returns (Sharpe ratio)
- Maximum drawdown management
- Consistency over time periods
- Learning and skill development

*Successful crypto trading combines technical analysis, fundamental research, risk management, and emotional discipline.*"""

    # Specific altcoins
    elif any(word in message_lower for word in ['altcoin', 'alt', 'best', 'top', 'recommend']):
        return f"""🚀 **Top Altcoin Analysis** • {timestamp}

**🏆 Tier 1 Altcoins (Established Leaders):**

**Solana (SOL)** - High-Performance Blockchain
• **Strengths**: Sub-second finality, low fees, growing DeFi/NFT ecosystem
• **Use Cases**: DeFi protocols, NFT marketplaces, Web3 applications
• **Investment Thesis**: Ethereum competitor with superior performance
• **Risks**: Network stability concerns, centralization questions

**Cardano (ADA)** - Research-Driven Blockchain  
• **Strengths**: Peer-reviewed development, sustainability focus
• **Use Cases**: Smart contracts, DeFi, African partnerships
• **Investment Thesis**: Long-term sustainable blockchain development
• **Risks**: Slow development pace, limited current utility

**Avalanche (AVAX)** - Subnet Architecture
• **Strengths**: Custom blockchain creation, enterprise adoption
• **Use Cases**: DeFi, gaming, enterprise applications
• **Investment Thesis**: Multi-chain future with specialized subnets
• **Risks**: Competition from other L1s, complexity

**🎯 Tier 2 Altcoins (Growth Potential):**

**Polygon (MATIC)** - Ethereum Scaling
• **Catalyst**: Growing enterprise partnerships, zkEVM rollout
• **Upside**: Ethereum ecosystem growth, corporate adoption

**Chainlink (LINK)** - Oracle Infrastructure
• **Catalyst**: Real-world data integration, cross-chain protocols
• **Upside**: Essential infrastructure for DeFi growth

**Polkadot (DOT)** - Interoperability
• **Catalyst**: Parachain ecosystem maturation
• **Upside**: Cross-chain communication solutions

**🔥 Emerging Sectors to Watch:**

**AI Integration:**
• Projects combining artificial intelligence with blockchain
• Decentralized AI training and inference
• Data monetization and privacy solutions

**Real World Assets (RWA):**
• Tokenization of traditional assets
• Real estate, commodities, bonds on blockchain
• Massive addressable market potential

**Gaming & Metaverse:**
• Play-to-earn game ecosystems
• Virtual world economies and NFTs
• Mass adoption through entertainment

**💡 Selection Criteria Framework:**

**Team & Development:**
- Experienced founders and developers
- Active GitHub commits and development
- Clear roadmap and execution history

**Technology & Innovation:**
- Unique value proposition or competitive advantage
- Scalable technology architecture
- Real-world problem solving

**Adoption & Partnerships:**
- Growing user base and transaction volume
- Enterprise partnerships and integrations
- Developer ecosystem growth

**Tokenomics:**
- Clear utility and value accrual mechanisms
- Reasonable token distribution and vesting
- Deflationary or growth-aligned economics

**⚠️ Altcoin Investment Strategy:**

**Diversification Rules:**
- Maximum 5-10% per individual altcoin
- Spread across different sectors and use cases
- Don't chase pumps or follow hype alone

**Research Process:**
1. Read whitepaper and understand technology
2. Analyze team backgrounds and experience
3. Study tokenomics and value accrual
4. Monitor development activity and partnerships
5. Assess competitive landscape and moats

**Risk Management:**
- Set stop losses for speculative positions
- Take profits during major rallies (50-80% gains)
- Rebalance portfolio quarterly
- Never invest more than you can afford to lose

*Altcoins offer higher growth potential but with significantly higher risk. Thorough research and diversification are essential.*"""

    # Profit calculator and financial calculations
    elif any(word in message_lower for word in ['profit', 'calculator', 'calculate', 'gains', 'loss', 'roi', 'return']):
        return f"""🧮 **Crypto Profit Calculator & Analysis** • {timestamp}

**💰 Comprehensive Profit/Loss Calculator:**

**📊 Investment Performance Metrics:**

**🎯 Basic Profit Calculation:**
• **Formula**: Profit = (Current Value - Initial Investment) - Fees
• **ROI %**: ((Current Value - Initial Investment) / Initial Investment) × 100
• **Annualized Return**: (Total Return / Years Held)^(1/Years) - 1

**💡 Example Calculations:**

**Bitcoin Investment Example:**
• **Initial Investment**: $10,000 at $40,000/BTC (0.25 BTC)
• **Current Price**: $100,000/BTC
• **Current Value**: $25,000
• **Profit**: $15,000
• **ROI**: 150%
• **If held 2 years**: 58.1% annualized return

**DCA Strategy Example:**
• **Monthly Investment**: $500 for 12 months
• **Total Invested**: $6,000
• **Average Buy Price**: $45,000/BTC
• **Current Price**: $100,000/BTC
• **Total BTC**: 0.133 BTC
• **Current Value**: $13,300
• **Profit**: $7,300 (121.7% ROI)

**🔧 Advanced Calculation Tools:**

**Position Sizing Calculator:**
• **Risk Per Trade**: 1-2% of portfolio
• **Stop Loss Distance**: Percentage from entry
• **Position Size**: (Risk Amount) ÷ (Stop Loss %)
• **Example**: $10k portfolio, 2% risk, 10% stop = $200 position

**DCA Calculator:**
• **Investment Amount**: Weekly/Monthly amount
• **Time Period**: Duration of DCA strategy
• **Price Averaging**: Weighted average purchase price
• **Total Cost**: Sum of all purchases + fees

**Yield Farming Calculator:**
• **Principal**: Initial staking amount
• **APY**: Annual percentage yield
• **Compounding**: Daily/Weekly/Monthly
• **Time**: Investment duration
• **Formula**: A = P(1 + r/n)^(nt)

**📈 Real-Time Calculation Features:**

**🎯 Quick Profit Check:**
1. **Enter Buy Price**: $____
2. **Enter Current Price**: $____
3. **Enter Amount Invested**: $____
4. **Add Trading Fees**: ___%
5. **Result**: Instant profit/loss calculation

**💸 Fee Impact Calculator:**
• **Trading Fees**: 0.1% - 1% per transaction
• **Network Fees**: Variable (ETH gas, BTC fees)
• **Spread Costs**: Bid-ask difference
• **Total Cost**: Can reduce returns by 2-5% annually

**🔮 Scenario Analysis:**

**Bull Case (+100%):**
• Investment doubles in value
• $10,000 → $20,000
• Net profit after fees: ~$9,800

**Base Case (+25%):**
• Moderate growth scenario  
• $10,000 → $12,500
• Net profit after fees: ~$2,400

**Bear Case (-50%):**
• Market downturn scenario
• $10,000 → $5,000
• Loss including fees: ~$5,100

**🛡️ Risk Management Calculations:**

**Portfolio Allocation:**
• **Conservative**: 5-10% crypto allocation
• **Moderate**: 10-20% crypto allocation  
• **Aggressive**: 20%+ crypto allocation

**Stop Loss Levels:**
• **Tight**: 10-15% below entry
• **Normal**: 20-25% below entry
• **Wide**: 30-40% below entry

**⚡ Interactive Calculator Commands:**

Say things like:
• "Calculate profit if Bitcoin hits $150,000"
• "What's my ROI on $5,000 investment?"
• "DCA calculator for $200 monthly"
• "Stop loss calculator for my position"
• "Yield farming returns on $10,000"

**💡 Pro Tips:**
- Always factor in taxes (20-37% on gains)
- Include all fees in calculations
- Use position sizing to manage risk
- Regular rebalancing improves returns
- Consider dollar-cost averaging for volatility

*This calculator helps you make informed investment decisions. Remember: past performance doesn't guarantee future results.*"""

    # API Routes
@app.get("/")
async def root():
    return {
        "message": "🚀 Crypto Analytics AI Backend is running!",
        "ai_status": "online" if AI_SERVICE_AVAILABLE else "fallback",
        "docs": "/docs"
    }

# Authentication Endpoints
@app.post("/api/auth/register", response_model=AuthResponse)
async def register_user_shortcut(user: UserRegistration):
    """Shortcut registration endpoint that frontend calls"""
    return await start_registration(user)

@app.post("/api/auth/register/start", response_model=AuthResponse)
async def start_registration(user: UserRegistration):
    """Start user registration process by sending OTP"""
    try:
        email = user.email.lower().strip()
        
        # Check if user already exists
        if email in verified_users:
            return AuthResponse(
                message="User already exists. Please login instead.",
                success=False
            )
        
        # Generate and store OTP
        otp = generate_otp()
        expiry_time = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        otp_storage[email] = {
            "otp": otp,
            "expiry": expiry_time,
            "type": "registration"
        }
        
        # Store pending registration
        pending_registrations[email] = {
            "email": email,
            "password_hash": hash_password(user.password),
            "created_at": datetime.now()
        }
        
        # Send OTP email
        if send_otp_email(email, otp):
            return AuthResponse(
                message=f"Registration started! OTP sent to {email}. Please verify to complete registration.",
                success=True
            )
        else:
            # Clean up if email sending failed
            if email in otp_storage:
                del otp_storage[email]
            if email in pending_registrations:
                del pending_registrations[email]
            
            raise HTTPException(status_code=500, detail="Failed to send OTP email")
            
    except Exception as e:
        print(f"❌ Registration start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/register/verify", response_model=AuthResponse)
async def register_verify(verification: OTPVerification):
    """Complete registration by verifying OTP"""
    try:
        email = verification.email.lower().strip()
        otp = verification.otp.strip()
        
        print(f"🔍 Registration verification for: {email}")
        print(f"📧 Pending registrations: {list(pending_registrations.keys())}")
        print(f"🔑 OTP storage: {list(otp_storage.keys())}")
        
        # Check if there's a pending registration
        if email not in pending_registrations:
            print(f"❌ No pending registration for {email}")
            raise HTTPException(status_code=400, detail="No pending registration found for this email")
        
        # Verify OTP
        if not verify_otp_code(email, otp):
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
        # Move from pending to verified users
        user_data = pending_registrations[email]
        verified_users[email] = {
            **user_data,
            "is_verified": True
        }
        
        # Clean up
        del pending_registrations[email]
        del otp_storage[email]
        
        print(f"✅ User {email} registration completed successfully!")
        
        # Generate JWT token
        token_payload = {
            "email": email,
            "exp": datetime.now() + timedelta(days=7)
        }
        token = jwt.encode(token_payload, "your_secret_key", algorithm="HS256")
        
        return AuthResponse(
            message="Registration completed successfully!",
            success=True,
            token=token,
            user={"email": email, "is_verified": True}
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Registration verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login", response_model=AuthResponse)
async def login_user(user: UserLogin):
    """Login user by sending OTP"""
    try:
        email = user.email.lower().strip()
        
        # Check if user exists and password is correct
        if email not in verified_users:
            raise HTTPException(status_code=400, detail="User not found. Please register first.")
        
        stored_user = verified_users[email]
        if stored_user["password_hash"] != hash_password(user.password):
            raise HTTPException(status_code=400, detail="Invalid password")
        
        # Generate and send OTP for login
        otp = generate_otp()
        expiry_time = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        otp_storage[email] = {
            "otp": otp,
            "expiry": expiry_time,
            "type": "login"
        }
        
        # Send OTP email
        if send_otp_email(email, otp):
            return AuthResponse(
                message=f"Login OTP sent to {email}. Please verify to continue.",
                success=True
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to send OTP email")
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/verify-otp", response_model=AuthResponse)
async def verify_login_otp(verification: OTPVerification):
    """Verify OTP for login"""
    try:
        email = verification.email.lower().strip()
        otp = verification.otp.strip()
        
        # Check if user exists
        if email not in verified_users:
            raise HTTPException(status_code=400, detail="User not found")
        
        # Verify OTP
        if not verify_otp_code(email, otp):
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
        # Clean up OTP
        if email in otp_storage:
            del otp_storage[email]
        
        # Generate JWT token
        token_payload = {
            "email": email,
            "exp": datetime.now() + timedelta(days=7)
        }
        token = jwt.encode(token_payload, "your_secret_key", algorithm="HS256")
        
        return AuthResponse(
            message="Login successful!",
            success=True,
            token=token,
            user={"email": email, "is_verified": True}
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ OTP verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ai/chat/health")
async def ai_health_check():
    return {
        "status": "healthy",
        "ai_service": "online" if AI_SERVICE_AVAILABLE else "fallback", 
        "message": "AI Chat service is running"
    }

@app.post("/api/v1/ai/chat", response_model=ChatResponse)
async def ai_chat(request: ChatMessage):
    """Main AI chat endpoint"""
    try:
        user_message = request.message
        context = request.user_context or {}
        
        # Try real AI first
        if AI_SERVICE_AVAILABLE:
            try:
                ai_response = await get_real_ai_response(user_message, context)
                return ChatResponse(
                    response=ai_response,
                    source="groq_ai",
                    suggestions=["Follow up", "More analysis", "Different perspective", "Technical details"]
                )
            except Exception as e:
                print(f"Real AI failed, using fallback: {e}")
        
        # Use enhanced fallback
        fallback_response = await get_enhanced_fallback_response(user_message, context)
        return ChatResponse(
            response=fallback_response,
            source="enhanced_fallback",
            suggestions=["Try again", "Bitcoin analysis", "Portfolio review", "Market trends"]
        )
        
    except Exception as e:
        print(f"Error in ai_chat: {e}")
        return ChatResponse(
            response=f"🚨 I'm experiencing technical difficulties: {str(e)}\n\nPlease try again in a moment.",
            source="error_fallback",
            suggestions=["Try again", "Check connection", "Restart service"]
        )

@app.post("/api/chat", response_model=ChatResponse)
async def chat_simplified(request: ChatMessage):
    """Simplified chat endpoint for frontend compatibility"""
    return await ai_chat(request)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.get("/api/v1/crypto/global-metrics")
async def get_global_metrics():
    """Get global crypto market metrics"""
    return {
        "status": "success",
        "data": {
            "total_market_cap": 2500000000000,  # $2.5T
            "total_volume_24h": 85000000000,    # $85B
            "bitcoin_dominance": 52.3,
            "ethereum_dominance": 17.8,
            "active_cryptocurrencies": 9500,
            "market_cap_change_24h": 2.1,
            "fear_greed_index": 72,
            "fear_greed_classification": "Greed"
        }
    }

@app.get("/api/v1/crypto/top-cryptos")
async def get_top_cryptos():
    """Get top cryptocurrencies"""
    return {
        "status": "success", 
        "data": [
            {
                "id": "bitcoin",
                "symbol": "BTC",
                "name": "Bitcoin",
                "price": 98500,
                "market_cap": 1950000000000,
                "volume_24h": 28000000000,
                "price_change_24h": 2.3,
                "price_change_7d": 8.7
            },
            {
                "id": "ethereum", 
                "symbol": "ETH",
                "name": "Ethereum",
                "price": 3650,
                "market_cap": 440000000000,
                "volume_24h": 15000000000,
                "price_change_24h": 1.8,
                "price_change_7d": 12.4
            },
            {
                "id": "solana",
                "symbol": "SOL", 
                "name": "Solana",
                "price": 245,
                "market_cap": 115000000000,
                "volume_24h": 3200000000,
                "price_change_24h": 4.2,
                "price_change_7d": 18.6
            }
        ]
    }

@app.get("/api/v1/crypto/portfolio/summary")
async def get_portfolio_summary():
    """Get portfolio summary"""
    return {
        "status": "success",
        "data": {
            "total_value": 0,
            "total_change_24h": 0,
            "total_change_7d": 0,
            "assets_count": 0,
            "top_performer": None,
            "worst_performer": None
        }
    }

@app.get("/api/market/data")
async def get_market_data():
    """Get global market data in the format expected by frontend"""
    return {
        "status": "success",
        "data": {
            "active_cryptocurrencies": 9847,
            "total_cryptocurrencies": 24123,
            "active_market_pairs": 89756,
            "active_exchanges": 756,
            "total_exchanges": 1234,
            "eth_dominance": 17.8,
            "btc_dominance": 52.3,
            "eth_dominance_yesterday": 17.6,
            "btc_dominance_yesterday": 52.1,
            "eth_dominance_24h_percentage_change": 1.14,
            "btc_dominance_24h_percentage_change": 0.38,
            "defi_volume_24h": 12500000000,
            "defi_volume_24h_reported": 12600000000,
            "defi_market_cap": 85000000000,
            "defi_24h_percentage_change": 2.5,
            "stablecoin_volume_24h": 45000000000,
            "stablecoin_volume_24h_reported": 45200000000,
            "stablecoin_market_cap": 125000000000,
            "stablecoin_24h_percentage_change": 0.1,
            "derivatives_volume_24h": 156000000000,
            "derivatives_volume_24h_reported": 156500000000,
            "derivatives_24h_percentage_change": 3.2,
            "quote": {
                "USD": {
                    "total_market_cap": 2500000000000,
                    "total_volume_24h": 85000000000,
                    "total_volume_24h_reported": 85500000000,
                    "altcoin_volume_24h": 45000000000,
                    "altcoin_volume_24h_reported": 45200000000,
                    "altcoin_market_cap": 1200000000000,
                    "defi_volume_24h": 12500000000,
                    "defi_volume_24h_reported": 12600000000,
                    "defi_24h_percentage_change": 2.5,
                    "defi_market_cap": 85000000000,
                    "stablecoin_volume_24h": 45000000000,
                    "stablecoin_volume_24h_reported": 45200000000,
                    "stablecoin_24h_percentage_change": 0.1,
                    "stablecoin_market_cap": 125000000000,
                    "derivatives_volume_24h": 156000000000,
                    "derivatives_volume_24h_reported": 156500000000,
                    "derivatives_24h_percentage_change": 3.2,
                    "total_market_cap_yesterday": 2450000000000,
                    "total_volume_24h_yesterday": 83000000000,
                    "total_market_cap_yesterday_percentage_change": 2.04,
                    "total_volume_24h_yesterday_percentage_change": 2.41,
                    "last_updated": "2024-12-28T10:30:00.000Z"
                }
            }
        }
    }

@app.post("/api/auth/resend-otp", response_model=AuthResponse)
async def resend_otp(user_info: Dict[str, Any]):
    """Resend OTP for user"""
    try:
        email = user_info.get("email", "").lower().strip()
        
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        # Check if user exists
        if email not in verified_users and email not in pending_registrations:
            raise HTTPException(status_code=400, detail="User not found")
        
        # Generate and store new OTP
        otp = generate_otp()
        expiry_time = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        otp_type = "registration" if email in pending_registrations else "login"
        otp_storage[email] = {
            "otp": otp,
            "expiry": expiry_time,
            "type": otp_type
        }
        
        # Send OTP email
        if send_otp_email(email, otp):
            return AuthResponse(
                message=f"New OTP sent to {email}",
                success=True
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to send OTP email")
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Resend OTP error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Crypto Analytics AI Backend...")
    print(f"📊 AI Service: {'✅ Online (Groq)' if AI_SERVICE_AVAILABLE else '⚠️ Fallback Mode'}")
    
    # Try different ports if 8000 is occupied
    ports_to_try = [8000, 8001, 8002, 8003, 8080]
    
    for port in ports_to_try:
        try:
            print(f"🌐 Trying to start server on http://localhost:{port}")
            print(f"📖 API docs will be available at http://localhost:{port}/docs")
            
            uvicorn.run(app, host="127.0.0.1", port=port, reload=False)
            break
        except OSError as e:
            if "WinError 10013" in str(e) or "Address already in use" in str(e):
                print(f"⚠️ Port {port} is already in use, trying next port...")
                continue
            else:
                print(f"❌ Error starting server on port {port}: {e}")
                continue
        except Exception as e:
            print(f"❌ Unexpected error on port {port}: {e}")
            continue
    else:
        print("❌ Could not start server on any available port!")
        print("💡 Try closing other applications that might be using these ports.")
        input("Press Enter to exit...")
