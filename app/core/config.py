"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    app_name: str = "Trading Dashboard"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database settings
    database_url: str = "sqlite:///./trading_dashboard.db"
    database_echo: bool = False
    
    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 300  # 5 minutes default TTL
    
    # JWT settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 hours
    
    # Upstox API settings
    upstox_api_key: Optional[str] = None
    upstox_api_secret: Optional[str] = None
    upstox_redirect_uri: Optional[str] = None
    upstox_base_url: str = "https://api.upstox.com/v2"
    
    # ML Model settings
    model_update_interval: int = 3600  # 1 hour in seconds
    prediction_confidence_threshold: float = 0.65
    
    # API Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()