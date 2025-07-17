import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "crypto_analytics"
    POSTGRES_PORT: str = "5432"
    
    DATABASE_URL: Optional[str] = None
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "https://localhost:3000",
    ]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # External APIs
    COINMARKETCAP_API_KEY: str = "your-coinmarketcap-api-key"
    COINMARKETCAP_BASE_URL: str = "https://pro-api.coinmarketcap.com/v1"
    
    NEWS_API_KEY: str = "your-news-api-key"
    NEWS_API_BASE_URL: str = "https://newsapi.org/v2"
    
    # AI/ML Settings
    MODEL_UPDATE_INTERVAL: int = 3600  # 1 hour in seconds
    PREDICTION_CACHE_TTL: int = 1800   # 30 minutes in seconds
    
    # Security
    ALGORITHM: str = "HS256"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
