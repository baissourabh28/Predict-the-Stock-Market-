"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator, Optional
import redis
from app.core.config import settings

# SQLAlchemy setup
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    poolclass=StaticPool if "sqlite" in settings.database_url else None,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for database models
Base = declarative_base()

# Redis setup with error handling
try:
    redis_client = redis.from_url(
        settings.redis_url, 
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    # Test connection
    redis_client.ping()
except (redis.ConnectionError, redis.TimeoutError) as e:
    import structlog
    logger = structlog.get_logger()
    logger.warning("Redis connection failed, caching will be disabled", error=str(e))
    redis_client = None


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis() -> Optional[redis.Redis]:
    """
    Get Redis client instance (may be None if Redis is unavailable)
    """
    return redis_client


# Database initialization
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)