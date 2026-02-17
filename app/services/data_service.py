"""
Data service for managing market data storage and retrieval
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import structlog

from app.models.market_data import MarketData, Prediction, TradingSignal
from app.schemas.market_data import CandlestickDataSchema, PredictionSchema, TradingSignalSchema
from app.services.yahoo_finance_service import YahooFinanceService, CandlestickData

logger = structlog.get_logger()


class DataService:
    """Service for managing market data operations"""
    
    def __init__(self):
        self.yahoo_service = YahooFinanceService()
    
    async def initialize(self):
        """Initialize the data service"""
        logger.info("Data service initialized with Yahoo Finance")
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Data service cleanup")
    
    def store_market_data(self, db: Session, data: CandlestickData) -> MarketData:
        """Store candlestick data in database"""
        try:
            # Check if data already exists
            existing = db.query(MarketData).filter(
                and_(
                    MarketData.symbol == data.symbol,
                    MarketData.timestamp == data.timestamp,
                    MarketData.timeframe == data.timeframe
                )
            ).first()
            
            if existing:
                # Update existing record
                existing.open_price = data.open_price
                existing.high_price = data.high_price
                existing.low_price = data.low_price
                existing.close_price = data.close_price
                existing.volume = data.volume
                db.commit()
                db.refresh(existing)
                return existing
            
            # Create new record
            db_data = MarketData(
                symbol=data.symbol,
                timestamp=data.timestamp,
                open_price=data.open_price,
                high_price=data.high_price,
                low_price=data.low_price,
                close_price=data.close_price,
                volume=data.volume,
                timeframe=data.timeframe
            )
            
            db.add(db_data)
            db.commit()
            db.refresh(db_data)
            
            logger.info("Stored market data", symbol=data.symbol, timestamp=data.timestamp)
            return db_data
            
        except Exception as e:
            logger.error("Failed to store market data", error=str(e))
            db.rollback()
            raise
    
    def get_market_data(
        self, 
        db: Session, 
        symbol: str, 
        timeframe: str, 
        limit: int = 100
    ) -> List[MarketData]:
        """Retrieve market data from database"""
        try:
            return db.query(MarketData).filter(
                and_(
                    MarketData.symbol == symbol,
                    MarketData.timeframe == timeframe
                )
            ).order_by(desc(MarketData.timestamp)).limit(limit).all()
            
        except Exception as e:
            logger.error("Failed to retrieve market data", error=str(e))
            return []
    
    def get_historical_data(
        self, 
        db: Session, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime, 
        timeframe: str
    ) -> List[MarketData]:
        """Retrieve historical market data"""
        try:
            return db.query(MarketData).filter(
                and_(
                    MarketData.symbol == symbol,
                    MarketData.timeframe == timeframe,
                    MarketData.timestamp >= start_date,
                    MarketData.timestamp <= end_date
                )
            ).order_by(MarketData.timestamp).all()
            
        except Exception as e:
            logger.error("Failed to retrieve historical data", error=str(e))
            return []
    
    async def fetch_and_store_live_data(
        self, 
        db: Session, 
        symbol: str, 
        timeframe: str = "1m"
    ) -> Optional[MarketData]:
        """Fetch live data from Yahoo Finance and store in database"""
        try:
            # Fetch from Yahoo Finance API
            live_data = await self.yahoo_service.get_live_quote(symbol, timeframe)
            
            if live_data:
                # Store in database
                return self.store_market_data(db, live_data)
            
            return None
            
        except Exception as e:
            logger.error("Failed to fetch and store live data", symbol=symbol, error=str(e))
            return None
    
    async def fetch_and_store_historical_data(
        self, 
        db: Session, 
        symbol: str, 
        days: int = 30, 
        timeframe: str = "1D"
    ) -> List[MarketData]:
        """Fetch historical data from Yahoo Finance and store in database"""
        try:
            # Fetch from Yahoo Finance API
            historical_data = await self.yahoo_service.get_historical_candles(symbol, days, timeframe)
            
            stored_data = []
            for data in historical_data:
                stored = self.store_market_data(db, data)
                if stored:
                    stored_data.append(stored)
            
            logger.info(
                "Fetched and stored historical data", 
                symbol=symbol, 
                records=len(stored_data)
            )
            return stored_data
            
        except Exception as e:
            logger.error("Failed to fetch and store historical data", symbol=symbol, error=str(e))
            return []
    
    def store_prediction(self, db: Session, prediction: PredictionSchema) -> Prediction:
        """Store ML prediction in database"""
        try:
            db_prediction = Prediction(
                symbol=prediction.symbol,
                predicted_price=prediction.predicted_price,
                confidence_score=prediction.confidence_score,
                time_horizon=prediction.time_horizon,
                timeframe=prediction.timeframe,
                model_used=prediction.model_used
            )
            
            db.add(db_prediction)
            db.commit()
            db.refresh(db_prediction)
            
            logger.info("Stored prediction", symbol=prediction.symbol, price=prediction.predicted_price)
            return db_prediction
            
        except Exception as e:
            logger.error("Failed to store prediction", error=str(e))
            db.rollback()
            raise
    
    def get_predictions(
        self, 
        db: Session, 
        symbol: str, 
        timeframe: str, 
        limit: int = 10
    ) -> List[Prediction]:
        """Retrieve predictions from database"""
        try:
            return db.query(Prediction).filter(
                and_(
                    Prediction.symbol == symbol,
                    Prediction.timeframe == timeframe
                )
            ).order_by(desc(Prediction.created_at)).limit(limit).all()
            
        except Exception as e:
            logger.error("Failed to retrieve predictions", error=str(e))
            return []
    
    def store_trading_signal(self, db: Session, signal: TradingSignalSchema) -> TradingSignal:
        """Store trading signal in database"""
        try:
            db_signal = TradingSignal(
                symbol=signal.symbol,
                signal_type=signal.signal_type,
                strength=signal.strength,
                price_target=signal.price_target,
                stop_loss=signal.stop_loss,
                support_level=signal.support_level,
                resistance_level=signal.resistance_level,
                timeframe=signal.timeframe,
                reasoning=signal.reasoning
            )
            
            db.add(db_signal)
            db.commit()
            db.refresh(db_signal)
            
            logger.info("Stored trading signal", symbol=signal.symbol, type=signal.signal_type)
            return db_signal
            
        except Exception as e:
            logger.error("Failed to store trading signal", error=str(e))
            db.rollback()
            raise
    
    def get_trading_signals(
        self, 
        db: Session, 
        symbol: str, 
        timeframe: str, 
        limit: int = 10
    ) -> List[TradingSignal]:
        """Retrieve trading signals from database"""
        try:
            return db.query(TradingSignal).filter(
                and_(
                    TradingSignal.symbol == symbol,
                    TradingSignal.timeframe == timeframe
                )
            ).order_by(desc(TradingSignal.created_at)).limit(limit).all()
            
        except Exception as e:
            logger.error("Failed to retrieve trading signals", error=str(e))
            return []
    
    def get_latest_price(self, db: Session, symbol: str, timeframe: str = "1m") -> Optional[float]:
        """Get the latest price for a symbol"""
        try:
            latest = db.query(MarketData).filter(
                and_(
                    MarketData.symbol == symbol,
                    MarketData.timeframe == timeframe
                )
            ).order_by(desc(MarketData.timestamp)).first()
            
            return latest.close_price if latest else None
            
        except Exception as e:
            logger.error("Failed to get latest price", symbol=symbol, error=str(e))
            return None
    
    async def get_multiple_live_quotes(
        self, 
        db: Session, 
        symbols: List[str], 
        timeframe: str = "1m"
    ) -> Dict[str, MarketData]:
        """Get live quotes for multiple symbols"""
        try:
            # Fetch from Yahoo Finance API
            quotes = await self.yahoo_service.get_multiple_quotes(symbols, timeframe)
            
            results = {}
            for symbol, data in quotes.items():
                # Store in database
                stored = self.store_market_data(db, data)
                if stored:
                    results[symbol] = stored
            
            return results
            
        except Exception as e:
            logger.error("Failed to get multiple live quotes", error=str(e))
            return {}