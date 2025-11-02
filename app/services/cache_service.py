"""
Redis caching service for market data and predictions
"""
import json
import pickle
from datetime import datetime, timedelta
from typing import Any, Optional, List, Dict
import redis
import structlog

from app.core.config import settings
from app.core.database import get_redis

logger = structlog.get_logger()


class CacheService:
    """Redis caching service with TTL and serialization support"""
    
    def __init__(self):
        self.redis_client = get_redis()
        self.default_ttl = settings.redis_cache_ttl
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for Redis storage"""
        try:
            if isinstance(data, (dict, list, str, int, float, bool)):
                return json.dumps(data, default=str).encode('utf-8')
            else:
                return pickle.dumps(data)
        except Exception as e:
            logger.error("Failed to serialize data", error=str(e))
            raise
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from Redis"""
        try:
            # Try JSON first (more efficient)
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fall back to pickle
                return pickle.loads(data)
        except Exception as e:
            logger.error("Failed to deserialize data", error=str(e))
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with optional TTL"""
        try:
            serialized_data = self._serialize_data(value)
            ttl = ttl or self.default_ttl
            
            result = self.redis_client.setex(key, ttl, serialized_data)
            
            if result:
                logger.debug("Cached data", key=key, ttl=ttl)
            
            return result
            
        except Exception as e:
            logger.error("Failed to set cache", key=key, error=str(e))
            return False
    
    def get(self, key: str) -> Any:
        """Get a value from cache"""
        try:
            data = self.redis_client.get(key)
            
            if data is None:
                return None
            
            result = self._deserialize_data(data)
            logger.debug("Cache hit", key=key)
            return result
            
        except Exception as e:
            logger.error("Failed to get from cache", key=key, error=str(e))
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        try:
            result = self.redis_client.delete(key)
            if result:
                logger.debug("Deleted from cache", key=key)
            return bool(result)
            
        except Exception as e:
            logger.error("Failed to delete from cache", key=key, error=str(e))
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error("Failed to check cache existence", key=key, error=str(e))
            return False
    
    def get_ttl(self, key: str) -> int:
        """Get TTL for a key"""
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error("Failed to get TTL", key=key, error=str(e))
            return -1
    
    def extend_ttl(self, key: str, ttl: int) -> bool:
        """Extend TTL for an existing key"""
        try:
            result = self.redis_client.expire(key, ttl)
            if result:
                logger.debug("Extended TTL", key=key, ttl=ttl)
            return result
        except Exception as e:
            logger.error("Failed to extend TTL", key=key, error=str(e))
            return False
    
    def get_keys_pattern(self, pattern: str) -> List[str]:
        """Get all keys matching a pattern"""
        try:
            return [key.decode('utf-8') for key in self.redis_client.keys(pattern)]
        except Exception as e:
            logger.error("Failed to get keys by pattern", pattern=pattern, error=str(e))
            return []
    
    def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                result = self.redis_client.delete(*keys)
                logger.info("Flushed keys by pattern", pattern=pattern, count=result)
                return result
            return 0
        except Exception as e:
            logger.error("Failed to flush keys by pattern", pattern=pattern, error=str(e))
            return 0


class MarketDataCache:
    """Specialized cache for market data operations"""
    
    def __init__(self):
        self.cache = CacheService()
    
    def _make_live_data_key(self, symbol: str, timeframe: str) -> str:
        """Generate cache key for live market data"""
        return f"live_data:{symbol}:{timeframe}"
    
    def _make_historical_data_key(self, symbol: str, timeframe: str, days: int) -> str:
        """Generate cache key for historical data"""
        return f"historical_data:{symbol}:{timeframe}:{days}"
    
    def _make_prediction_key(self, symbol: str, timeframe: str, time_horizon: str) -> str:
        """Generate cache key for predictions"""
        return f"prediction:{symbol}:{timeframe}:{time_horizon}"
    
    def _make_signal_key(self, symbol: str, timeframe: str) -> str:
        """Generate cache key for trading signals"""
        return f"signal:{symbol}:{timeframe}"
    
    def cache_live_data(self, symbol: str, timeframe: str, data: Dict, ttl: int = 60) -> bool:
        """Cache live market data with short TTL"""
        key = self._make_live_data_key(symbol, timeframe)
        return self.cache.set(key, data, ttl)
    
    def get_live_data(self, symbol: str, timeframe: str) -> Optional[Dict]:
        """Get cached live market data"""
        key = self._make_live_data_key(symbol, timeframe)
        return self.cache.get(key)
    
    def cache_historical_data(self, symbol: str, timeframe: str, days: int, data: List[Dict], ttl: int = 1800) -> bool:
        """Cache historical data with longer TTL (30 minutes)"""
        key = self._make_historical_data_key(symbol, timeframe, days)
        return self.cache.set(key, data, ttl)
    
    def get_historical_data(self, symbol: str, timeframe: str, days: int) -> Optional[List[Dict]]:
        """Get cached historical data"""
        key = self._make_historical_data_key(symbol, timeframe, days)
        return self.cache.get(key)
    
    def cache_prediction(self, symbol: str, timeframe: str, time_horizon: str, prediction: Dict, ttl: int = 600) -> bool:
        """Cache ML prediction with medium TTL (10 minutes)"""
        key = self._make_prediction_key(symbol, timeframe, time_horizon)
        return self.cache.set(key, prediction, ttl)
    
    def get_prediction(self, symbol: str, timeframe: str, time_horizon: str) -> Optional[Dict]:
        """Get cached prediction"""
        key = self._make_prediction_key(symbol, timeframe, time_horizon)
        return self.cache.get(key)
    
    def cache_trading_signal(self, symbol: str, timeframe: str, signal: Dict, ttl: int = 300) -> bool:
        """Cache trading signal with short TTL (5 minutes)"""
        key = self._make_signal_key(symbol, timeframe)
        return self.cache.set(key, signal, ttl)
    
    def get_trading_signal(self, symbol: str, timeframe: str) -> Optional[Dict]:
        """Get cached trading signal"""
        key = self._make_signal_key(symbol, timeframe)
        return self.cache.get(key)
    
    def invalidate_symbol_cache(self, symbol: str) -> int:
        """Invalidate all cached data for a symbol"""
        pattern = f"*:{symbol}:*"
        return self.cache.flush_pattern(pattern)
    
    def warm_cache_for_symbols(self, symbols: List[str], timeframes: List[str]) -> None:
        """Warm cache for popular symbols and timeframes"""
        logger.info("Starting cache warming", symbols=symbols, timeframes=timeframes)
        
        # This would typically fetch and cache data for popular symbols
        # Implementation depends on your data fetching strategy
        for symbol in symbols:
            for timeframe in timeframes:
                # Check if data exists in cache
                if not self.get_live_data(symbol, timeframe):
                    logger.debug("Cache miss during warming", symbol=symbol, timeframe=timeframe)
                    # Here you would fetch and cache the data
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = self.cache.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info),
            }
        except Exception as e:
            logger.error("Failed to get cache stats", error=str(e))
            return {}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calculate cache hit rate"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return round((hits / total) * 100, 2)