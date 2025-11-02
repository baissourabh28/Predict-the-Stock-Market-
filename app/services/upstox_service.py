"""
Upstox API integration service for fetching market data
"""
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import structlog

from app.core.config import settings

logger = structlog.get_logger()


@dataclass
class CandlestickData:
    """Candlestick data structure"""
    symbol: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    timeframe: str


class UpstoxConnector:
    """Upstox API connector with rate limiting and error handling"""
    
    def __init__(self):
        self.base_url = settings.upstox_base_url
        self.api_key = settings.upstox_api_key
        self.api_secret = settings.upstox_api_secret
        self.access_token = None
        self.session = None
        self.rate_limiter = asyncio.Semaphore(10)  # Max 10 concurrent requests
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """Make HTTP request with rate limiting and error handling"""
        async with self.rate_limiter:
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 429:  # Rate limit exceeded
                        logger.warning("Rate limit exceeded, waiting...")
                        await asyncio.sleep(1)
                        return await self._make_request(method, endpoint, params, data)
                    
                    response.raise_for_status()
                    return await response.json()
                    
            except aiohttp.ClientError as e:
                logger.error("HTTP request failed", error=str(e), endpoint=endpoint)
                raise
            except asyncio.TimeoutError:
                logger.error("Request timeout", endpoint=endpoint)
                raise
    
    async def authenticate(self, code: str = None) -> bool:
        """Authenticate with Upstox API"""
        # For demo purposes, we'll simulate authentication
        # In production, implement OAuth2 flow with Upstox
        logger.info("Simulating Upstox authentication")
        self.access_token = "demo_token_12345"
        return True
    
    async def get_live_data(self, symbol: str, timeframe: str = "1m") -> Optional[CandlestickData]:
        """Fetch live candlestick data for a symbol"""
        try:
            # Simulate API call - replace with actual Upstox API endpoint
            # endpoint = f"/market-quote/ohlc"
            # params = {"instrument_key": symbol}
            # response = await self._make_request("GET", endpoint, params)
            
            # For demo, generate mock data
            mock_data = self._generate_mock_candlestick(symbol, timeframe)
            
            logger.info("Fetched live data", symbol=symbol, timeframe=timeframe)
            return mock_data
            
        except Exception as e:
            logger.error("Failed to fetch live data", symbol=symbol, error=str(e))
            return None
    
    async def get_historical_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime, 
        timeframe: str = "1D"
    ) -> List[CandlestickData]:
        """Fetch historical candlestick data"""
        try:
            # Simulate API call - replace with actual Upstox API endpoint
            # endpoint = f"/historical-candle/{symbol}/{timeframe}/{end_date}/{start_date}"
            # response = await self._make_request("GET", endpoint)
            
            # For demo, generate mock historical data
            mock_data = self._generate_mock_historical_data(symbol, start_date, end_date, timeframe)
            
            logger.info(
                "Fetched historical data", 
                symbol=symbol, 
                timeframe=timeframe,
                records=len(mock_data)
            )
            return mock_data
            
        except Exception as e:
            logger.error("Failed to fetch historical data", symbol=symbol, error=str(e))
            return []
    
    def _generate_mock_candlestick(self, symbol: str, timeframe: str) -> CandlestickData:
        """Generate mock candlestick data for demo purposes"""
        import random
        
        # More realistic base prices
        base_prices = {
            "NIFTY50": 19500.0,
            "SENSEX": 65000.0,
            "RELIANCE": 2500.0,
            "TCS": 3500.0,
            "INFY": 1400.0,
            "HDFC": 1600.0,
            "ICICIBANK": 950.0,
            "TATASTEEL": 120.0,
            "WIPRO": 400.0,
            "HDFCBANK": 1650.0
        }
        
        base_price = base_prices.get(symbol.upper(), 100.0)
        
        # Add some trending behavior
        trend_factor = random.uniform(0.98, 1.02)  # ±2% trend
        base_price *= trend_factor
        
        # Generate realistic OHLC data with proper relationships
        volatility = 0.015  # 1.5% volatility
        open_price = base_price * (1 + random.uniform(-volatility, volatility))
        
        # High and low should respect open price
        high_range = random.uniform(0.005, 0.02)  # 0.5% to 2% above open
        low_range = random.uniform(0.005, 0.02)   # 0.5% to 2% below open
        
        high_price = open_price * (1 + high_range)
        low_price = open_price * (1 - low_range)
        
        # Close price should be between high and low
        close_price = low_price + (high_price - low_price) * random.random()
        
        # Volume based on symbol type
        if "NIFTY" in symbol.upper() or "SENSEX" in symbol.upper():
            volume = random.randint(50000, 200000)
        else:
            volume = random.randint(100000, 2000000)
        
        return CandlestickData(
            symbol=symbol,
            timestamp=datetime.now(),
            open_price=round(open_price, 2),
            high_price=round(high_price, 2),
            low_price=round(low_price, 2),
            close_price=round(close_price, 2),
            volume=volume,
            timeframe=timeframe
        )
    
    def _generate_mock_historical_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime, 
        timeframe: str
    ) -> List[CandlestickData]:
        """Generate mock historical data for demo purposes"""
        import random
        
        data = []
        current_date = start_date
        base_price = 100.0
        
        if "NIFTY" in symbol.upper():
            base_price = 19500.0
        elif "SENSEX" in symbol.upper():
            base_price = 65000.0
        elif "RELIANCE" in symbol.upper():
            base_price = 2500.0
        
        # Determine time delta based on timeframe
        if timeframe == "1m":
            delta = timedelta(minutes=1)
        elif timeframe == "5m":
            delta = timedelta(minutes=5)
        elif timeframe == "15m":
            delta = timedelta(minutes=15)
        elif timeframe == "1H":
            delta = timedelta(hours=1)
        elif timeframe == "1D":
            delta = timedelta(days=1)
        else:
            delta = timedelta(days=1)
        
        current_price = base_price
        
        while current_date <= end_date:
            # Generate realistic price movement
            price_change = random.uniform(-2, 2)  # ±2% change
            current_price *= (1 + price_change / 100)
            
            open_price = current_price
            high_price = open_price * (1 + random.uniform(0, 0.01))  # Up to 1% higher
            low_price = open_price * (1 - random.uniform(0, 0.01))   # Up to 1% lower
            close_price = open_price + random.uniform(-5, 5)
            volume = random.randint(10000, 1000000)
            
            data.append(CandlestickData(
                symbol=symbol,
                timestamp=current_date,
                open_price=round(open_price, 2),
                high_price=round(high_price, 2),
                low_price=round(low_price, 2),
                close_price=round(close_price, 2),
                volume=volume,
                timeframe=timeframe
            ))
            
            current_date += delta
            current_price = close_price
        
        return data


class UpstoxService:
    """High-level service for Upstox operations"""
    
    def __init__(self):
        self.connector = None
    
    async def initialize(self):
        """Initialize the service"""
        self.connector = UpstoxConnector()
        await self.connector.__aenter__()
        
        # Authenticate if credentials are available
        if settings.upstox_api_key and settings.upstox_api_secret:
            await self.connector.authenticate()
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.connector:
            await self.connector.__aexit__(None, None, None)
    
    async def get_live_quote(self, symbol: str, timeframe: str = "1m") -> Optional[CandlestickData]:
        """Get live market quote"""
        if not self.connector:
            await self.initialize()
        
        return await self.connector.get_live_data(symbol, timeframe)
    
    async def get_historical_candles(
        self, 
        symbol: str, 
        days: int = 30, 
        timeframe: str = "1D"
    ) -> List[CandlestickData]:
        """Get historical candlestick data"""
        if not self.connector:
            await self.initialize()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return await self.connector.get_historical_data(symbol, start_date, end_date, timeframe)
    
    async def get_multiple_quotes(self, symbols: List[str], timeframe: str = "1m") -> Dict[str, CandlestickData]:
        """Get live quotes for multiple symbols"""
        if not self.connector:
            await self.initialize()
        
        results = {}
        tasks = []
        
        for symbol in symbols:
            task = self.connector.get_live_data(symbol, timeframe)
            tasks.append((symbol, task))
        
        # Execute all requests concurrently
        for symbol, task in tasks:
            try:
                data = await task
                if data:
                    results[symbol] = data
            except Exception as e:
                logger.error("Failed to fetch data for symbol", symbol=symbol, error=str(e))
        
        return results