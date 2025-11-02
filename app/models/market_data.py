"""
Market data models for storing candlestick data and predictions
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Index
from sqlalchemy.sql import func
from app.core.database import Base


class MarketData(Base):
    """Market data model for candlestick information"""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    timeframe = Column(String(10), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp'),
    )

    def __repr__(self):
        return f"<MarketData(symbol='{self.symbol}', timestamp='{self.timestamp}', close={self.close_price})>"


class Prediction(Base):
    """ML prediction model"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    predicted_price = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    time_horizon = Column(String(20), nullable=False)  # short, medium, long
    timeframe = Column(String(10), nullable=False)
    model_used = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<Prediction(symbol='{self.symbol}', price={self.predicted_price}, confidence={self.confidence_score})>"


class TradingSignal(Base):
    """Trading signal model"""
    __tablename__ = "trading_signals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    signal_type = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    strength = Column(Float, nullable=False)  # 0.0 to 1.0
    price_target = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    support_level = Column(Float, nullable=True)
    resistance_level = Column(Float, nullable=True)
    timeframe = Column(String(10), nullable=False)
    reasoning = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<TradingSignal(symbol='{self.symbol}', type='{self.signal_type}', strength={self.strength})>"