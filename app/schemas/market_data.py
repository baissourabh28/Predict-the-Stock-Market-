"""
Pydantic schemas for market data operations
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TimeframeEnum(str, Enum):
    """Supported timeframes"""
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1H"
    ONE_DAY = "1D"
    ONE_WEEK = "1W"


class SignalTypeEnum(str, Enum):
    """Trading signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class TimeHorizonEnum(str, Enum):
    """Prediction time horizons"""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class CandlestickDataSchema(BaseModel):
    """Schema for candlestick data"""
    symbol: str = Field(..., min_length=1, max_length=50)
    timestamp: datetime
    open_price: float = Field(..., gt=0)
    high_price: float = Field(..., gt=0)
    low_price: float = Field(..., gt=0)
    close_price: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)
    timeframe: TimeframeEnum

    @validator('high_price')
    def validate_high_price(cls, v, values):
        if 'open_price' in values and 'low_price' in values:
            if v < values['low_price']:
                raise ValueError('High price must be >= low price')
        return v

    @validator('low_price')
    def validate_low_price(cls, v, values):
        if 'open_price' in values:
            if v > values['open_price']:
                # Allow but don't enforce - market can gap down
                pass
        return v

    class Config:
        from_attributes = True


class MarketDataResponse(CandlestickDataSchema):
    """Response schema for market data"""
    id: int
    created_at: datetime


class PredictionSchema(BaseModel):
    """Schema for ML predictions"""
    symbol: str = Field(..., min_length=1, max_length=50)
    predicted_price: float = Field(..., gt=0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    time_horizon: TimeHorizonEnum
    timeframe: TimeframeEnum
    model_used: str = Field(..., min_length=1, max_length=50)

    class Config:
        from_attributes = True


class PredictionResponse(PredictionSchema):
    """Response schema for predictions"""
    id: int
    created_at: datetime


class TradingSignalSchema(BaseModel):
    """Schema for trading signals"""
    symbol: str = Field(..., min_length=1, max_length=50)
    signal_type: SignalTypeEnum
    strength: float = Field(..., ge=0.0, le=1.0)
    price_target: Optional[float] = Field(None, gt=0)
    stop_loss: Optional[float] = Field(None, gt=0)
    support_level: Optional[float] = Field(None, gt=0)
    resistance_level: Optional[float] = Field(None, gt=0)
    timeframe: TimeframeEnum
    reasoning: Optional[str] = Field(None, max_length=500)

    class Config:
        from_attributes = True


class TradingSignalResponse(TradingSignalSchema):
    """Response schema for trading signals"""
    id: int
    created_at: datetime


class MarketDataRequest(BaseModel):
    """Request schema for market data"""
    symbol: str = Field(..., min_length=1, max_length=50)
    timeframe: TimeframeEnum = TimeframeEnum.ONE_DAY
    days: int = Field(30, ge=1, le=365)


class MultipleSymbolsRequest(BaseModel):
    """Request schema for multiple symbols"""
    symbols: List[str] = Field(..., min_items=1, max_items=20)
    timeframe: TimeframeEnum = TimeframeEnum.ONE_MINUTE


class HistoricalDataRequest(BaseModel):
    """Request schema for historical data"""
    symbol: str = Field(..., min_length=1, max_length=50)
    start_date: datetime
    end_date: datetime
    timeframe: TimeframeEnum = TimeframeEnum.ONE_DAY

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class PredictionRequest(BaseModel):
    """Request schema for generating predictions"""
    symbol: str = Field(..., min_length=1, max_length=50)
    timeframe: TimeframeEnum = TimeframeEnum.ONE_DAY
    time_horizon: TimeHorizonEnum = TimeHorizonEnum.SHORT


class SignalRequest(BaseModel):
    """Request schema for generating trading signals"""
    symbol: str = Field(..., min_length=1, max_length=50)
    timeframe: TimeframeEnum = TimeframeEnum.ONE_DAY