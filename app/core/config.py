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
    debug: bool = True  # Set to False in production
    
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
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-CHANGE-IN-PRODUCTION-OR-APP-WILL-NOT-START")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 hours
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate secret key in production
        if not self.debug and self.secret_key == "dev-secret-key-CHANGE-IN-PRODUCTION-OR-APP-WILL-NOT-START":
            raise ValueError(
                "SECRET_KEY environment variable must be set in production! "
                "Generate a secure key with: openssl rand -hex 32"
            )
    
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