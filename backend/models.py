"""
Database models for Crypto Analytics Platform
PostgreSQL implementation with SQLAlchemy
"""

from sqlalchemy import Column, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="owner")
    alerts = relationship("Alert", back_populates="user")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String, nullable=False, default="My Portfolio")
    total_value = Column(Float, default=0.0)
    total_change_24h = Column(Float, default=0.0)
    assets_data = Column(Text)  # JSON string of portfolio assets
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="portfolios")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    crypto_symbol = Column(String, nullable=False)  # BTC, ETH, etc.
    alert_type = Column(String, nullable=False)  # price, volume, percentage
    condition = Column(String, nullable=False)  # above, below
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="alerts")

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    theme = Column(String, default="dark")  # dark, light
    currency = Column(String, default="USD")  # USD, EUR, etc.
    notifications_enabled = Column(Boolean, default=True)
    email_alerts = Column(Boolean, default=True)
    favorite_cryptos = Column(Text)  # JSON string of favorite crypto symbols
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences")

class TradingSignal(Base):
    __tablename__ = "trading_signals"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    crypto_symbol = Column(String, nullable=False)
    signal_type = Column(String, nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    price_target = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    technical_indicators = Column(Text)  # JSON string of indicators
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    source = Column(String, nullable=False)
    url = Column(String, nullable=True)
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    sentiment_label = Column(String, nullable=True)  # BULLISH, BEARISH, NEUTRAL
    related_cryptos = Column(Text)  # JSON string of related crypto symbols
    published_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
