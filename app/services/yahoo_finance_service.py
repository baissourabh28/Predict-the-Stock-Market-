"""
Yahoo Finance integration for real stock market data
Free API without authentication required
"""
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import structlog
import pandas as pd

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


class YahooFinanceService:
    """Service for fetching real market data from Yahoo Finance"""
    
    # Indian stock symbols mapping
    INDIAN_SYMBOLS = {
        'RELIANCE': 'RELIANCE.NS',
        'TCS': 'TCS.NS',
        'INFY': 'INFY.NS',
        'HDFC': 'HDFCBANK.NS',
        'HDFCBANK': 'HDFCBANK.NS',
        'ICICIBANK': 'ICICIBANK.NS',
        'SBIN': 'SBIN.NS',
        'BHARTIARTL': 'BHARTIARTL.NS',
        'ITC': 'ITC.NS',
        'HINDUNILVR': 'HINDUNILVR.NS',
        'KOTAKBANK': 'KOTAKBANK.NS',
        'LT': 'LT.NS',
        'ASIANPAINT': 'ASIANPAINTS.NS',
        'MARUTI': 'MARUTI.NS',
        'HCLTECH': 'HCLTECH.NS',
        'AXISBANK': 'AXISBANK.NS',
        'ULTRACEMCO': 'ULTRACEMCO.NS',
        'SUNPHARMA': 'SUNPHARMA.NS',
        'TITAN': 'TITAN.NS',
        'WIPRO': 'WIPRO.NS',
        'TECHM': 'TECHM.NS',
        'POWERGRID': 'POWERGRID.NS',
        'NTPC': 'NTPC.NS',
        'ONGC': 'ONGC.NS',
        'COALINDIA': 'COALINDIA.NS',
        'TATAMOTORS': 'TATAMOTORS.NS',
        'TATASTEEL': 'TATASTEEL.NS',
        'JSWSTEEL': 'JSWSTEEL.NS',
        'HINDALCO': 'HINDALCO.NS',
        'NIFTY50': '^NSEI',
        'SENSEX': '^BSESN',
    }
    
    TIMEFRAME_MAPPING = {
        '1m': '1m',
        '5m': '5m',
        '15m': '15m',
        '1H': '1h',
        '1D': '1d',
        '1W': '1wk',
    }
    
    def __init__(self):
        self.cache = {}
        logger.info("Yahoo Finance service initialized")
    
    def _get_yahoo_symbol(self, symbol: str) -> str:
        """Convert symbol to Yahoo Finance format"""
        symbol = symbol.upper()
        return self.INDIAN_SYMBOLS.get(symbol, f"{symbol}.NS")
    
    def _get_yahoo_interval(self, timeframe: str) -> str:
        """Convert timeframe to Yahoo Finance interval"""
        return self.TIMEFRAME_MAPPING.get(timeframe, '1d')
    
    async def get_live_quote(self, symbol: str, timeframe: str = "1m") -> Optional[CandlestickData]:
        """Fetch live market quote"""
        try:
            yahoo_symbol = self._get_yahoo_symbol(symbol)
            logger.info("Fetching live quote", symbol=symbol, yahoo_symbol=yahoo_symbol)
            
            # Get ticker
            ticker = yf.Ticker(yahoo_symbol)
            
            # Get latest data
            interval = self._get_yahoo_interval(timeframe)
            period = '1d' if interval in ['1m', '5m', '15m'] else '5d'
            
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning("No data returned", symbol=symbol)
                return None
            
            # Get the latest candle
            latest = df.iloc[-1]
            
            candle = CandlestickData(
                symbol=symbol,
                timestamp=latest.name.to_pydatetime() if hasattr(latest.name, 'to_pydatetime') else datetime.now(),
                open_price=float(latest['Open']),
                high_price=float(latest['High']),
                low_price=float(latest['Low']),
                close_price=float(latest['Close']),
                volume=int(latest['Volume']),
                timeframe=timeframe
            )
            
            logger.info("Live quote fetched successfully", 
                       symbol=symbol, 
                       price=candle.close_price)
            
            return candle
            
        except Exception as e:
            logger.error("Failed to fetch live quote", symbol=symbol, error=str(e))
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
            yahoo_symbol = self._get_yahoo_symbol(symbol)
            interval = self._get_yahoo_interval(timeframe)
            
            logger.info("Fetching historical data", 
                       symbol=symbol,
                       start=start_date,
                       end=end_date,
                       interval=interval)
            
            # Get ticker
            ticker = yf.Ticker(yahoo_symbol)
            
            # Fetch historical data
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )
            
            if df.empty:
                logger.warning("No historical data returned", symbol=symbol)
                return []
            
            # Convert to CandlestickData list
            candles = []
            for index, row in df.iterrows():
                candle = CandlestickData(
                    symbol=symbol,
                    timestamp=index.to_pydatetime() if hasattr(index, 'to_pydatetime') else datetime.now(),
                    open_price=float(row['Open']),
                    high_price=float(row['High']),
                    low_price=float(row['Low']),
                    close_price=float(row['Close']),
                    volume=int(row['Volume']),
                    timeframe=timeframe
                )
                candles.append(candle)
            
            logger.info("Historical data fetched successfully",
                       symbol=symbol,
                       records=len(candles))
            
            return candles
            
        except Exception as e:
            logger.error("Failed to fetch historical data", symbol=symbol, error=str(e))
            return []
    
    async def get_historical_candles(
        self, 
        symbol: str, 
        days: int = 30, 
        timeframe: str = "1D"
    ) -> List[CandlestickData]:
        """Get historical candles for specified number of days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return await self.get_historical_data(symbol, start_date, end_date, timeframe)
    
    async def get_multiple_quotes(
        self, 
        symbols: List[str], 
        timeframe: str = "1m"
    ) -> Dict[str, CandlestickData]:
        """Get live quotes for multiple symbols"""
        results = {}
        
        for symbol in symbols:
            try:
                data = await self.get_live_quote(symbol, timeframe)
                if data:
                    results[symbol] = data
            except Exception as e:
                logger.error("Failed to fetch quote for symbol", symbol=symbol, error=str(e))
        
        return results
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get market status"""
        now = datetime.now()
        hour = now.hour
        day = now.weekday()  # 0 = Monday, 6 = Sunday
        
        # NSE trading hours: 9:15 AM to 3:30 PM IST, Monday to Friday
        is_open = (day < 5) and (9 <= hour < 16)
        
        if is_open:
            status = "OPEN"
            message = "Market is open"
        elif day >= 5:
            status = "CLOSED"
            message = "Weekend - Market closed"
        elif hour < 9:
            status = "PRE_MARKET"
            message = "Pre-market session"
        else:
            status = "CLOSED"
            message = "Market closed for the day"
        
        return {
            "status": status,
            "message": message,
            "timestamp": now.isoformat()
        }
