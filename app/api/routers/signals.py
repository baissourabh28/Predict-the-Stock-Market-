"""
Trading Signals API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.market_data import SignalRequest, TradingSignalResponse, TradingSignalSchema
from app.services.data_service import DataService
from app.services.signal_service import SignalGenerator, RiskManager
from app.services.cache_service import MarketDataCache
from app.models.user import User

router = APIRouter(prefix="/signals", tags=["Trading Signals"])

# Initialize services
data_service = DataService()
signal_generator = SignalGenerator()
risk_manager = RiskManager()
cache_service = MarketDataCache()


@router.post("/generate", response_model=Dict[str, Any])
async def generate_trading_signal(
    request: SignalRequest,
    include_ml_prediction: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate trading signal for a symbol"""
    try:
        # Check cache first
        cached_signal = cache_service.get_trading_signal(request.symbol, request.timeframe)
        if cached_signal:
            return {
                "symbol": request.symbol,
                "timeframe": request.timeframe,
                "signal": cached_signal,
                "source": "cache",
                "timestamp": datetime.now()
            }
        
        # Get market data
        market_data = data_service.get_market_data(
            db, request.symbol, request.timeframe, limit=100
        )
        
        if len(market_data) < 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient data for signal generation. Need at least 20 records, got {len(market_data)}"
            )
        
        # Get ML prediction if requested
        ml_prediction = None
        if include_ml_prediction:
            try:
                # Try to get cached prediction first
                ml_prediction = cache_service.get_prediction(
                    request.symbol, request.timeframe, "short"
                )
                
                # If no cached prediction, generate one
                if not ml_prediction:
                    from app.services.ml_service import PredictionEngine
                    prediction_engine = PredictionEngine()
                    ml_prediction = prediction_engine.generate_prediction(
                        market_data, request.symbol, request.timeframe, "short"
                    )
            except Exception as e:
                # Continue without ML prediction if it fails
                pass
        
        # Generate signals
        signal_result = signal_generator.generate_signals(
            market_data, ml_prediction, request.timeframe
        )
        
        # Apply risk management
        filtered_signal = risk_manager.apply_risk_filters(signal_result, market_data)
        
        # Store signal in database
        signal_schema = TradingSignalSchema(
            symbol=request.symbol,
            signal_type=filtered_signal['signal_type'],
            strength=filtered_signal['strength'],
            price_target=filtered_signal.get('price_target'),
            stop_loss=filtered_signal.get('stop_loss'),
            support_level=filtered_signal.get('support_levels', [None])[0] if filtered_signal.get('support_levels') else None,
            resistance_level=filtered_signal.get('resistance_levels', [None])[0] if filtered_signal.get('resistance_levels') else None,
            timeframe=request.timeframe,
            reasoning=filtered_signal.get('reasoning', '')
        )
        
        stored_signal = data_service.store_trading_signal(db, signal_schema)
        
        # Add additional information to response
        response_signal = {
            **filtered_signal,
            "signal_id": stored_signal.id,
            "generated_at": stored_signal.created_at,
            "ml_prediction_included": ml_prediction is not None
        }
        
        # Cache the signal
        cache_service.cache_trading_signal(
            request.symbol, request.timeframe, response_signal, ttl=300
        )
        
        return {
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "signal": response_signal,
            "source": "generated",
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate trading signal: {str(e)}"
        )


@router.get("/history/{symbol}", response_model=List[TradingSignalResponse])
async def get_signal_history(
    symbol: str,
    timeframe: str = "1D",
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trading signal history for a symbol"""
    try:
        signals = data_service.get_trading_signals(db, symbol, timeframe, limit)
        return signals
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get signal history: {str(e)}"
        )


@router.get("/support-resistance/{symbol}")
async def get_support_resistance_levels(
    symbol: str,
    timeframe: str = "1D",
    lookback_periods: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get support and resistance levels for a symbol"""
    try:
        # Get market data
        market_data = data_service.get_market_data(
            db, symbol, timeframe, limit=lookback_periods
        )
        
        if len(market_data) < 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient data for support/resistance calculation. Need at least 20 records, got {len(market_data)}"
            )
        
        # Calculate support and resistance levels
        from app.services.signal_service import SupportResistanceCalculator
        sr_calculator = SupportResistanceCalculator()
        sr_levels = sr_calculator.calculate_support_resistance(market_data, lookback_periods)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "lookback_periods": lookback_periods,
            "current_price": sr_levels.get('current_price'),
            "support_levels": sr_levels.get('support_levels', []),
            "resistance_levels": sr_levels.get('resistance_levels', []),
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate support/resistance levels: {str(e)}"
        )


@router.get("/technical-analysis/{symbol}")
async def get_technical_analysis(
    symbol: str,
    timeframe: str = "1D",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive technical analysis for a symbol"""
    try:
        # Get market data
        market_data = data_service.get_market_data(
            db, symbol, timeframe, limit=100
        )
        
        if len(market_data) < 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient data for technical analysis. Need at least 20 records, got {len(market_data)}"
            )
        
        # Generate technical signals (without final signal generation)
        import pandas as pd
        df = pd.DataFrame([{
            'timestamp': data.timestamp,
            'open_price': data.open_price,
            'high_price': data.high_price,
            'low_price': data.low_price,
            'close_price': data.close_price,
            'volume': data.volume
        } for data in market_data])
        
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Calculate technical indicators
        technical_signals = signal_generator._calculate_technical_signals(df)
        
        # Get support/resistance levels
        from app.services.signal_service import SupportResistanceCalculator
        sr_calculator = SupportResistanceCalculator()
        sr_levels = sr_calculator.calculate_support_resistance(market_data)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": df['close_price'].iloc[-1],
            "technical_indicators": technical_signals,
            "support_resistance": sr_levels,
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get technical analysis: {str(e)}"
        )


@router.get("/signal-strength/{symbol}")
async def get_signal_strength_breakdown(
    symbol: str,
    timeframe: str = "1D",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed signal strength breakdown"""
    try:
        # Get latest signal
        signals = data_service.get_trading_signals(db, symbol, timeframe, limit=1)
        
        if not signals:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No signals found for symbol {symbol}"
            )
        
        latest_signal = signals[0]
        
        # Get market data for detailed analysis
        market_data = data_service.get_market_data(
            db, symbol, timeframe, limit=50
        )
        
        # Generate fresh technical analysis
        import pandas as pd
        df = pd.DataFrame([{
            'timestamp': data.timestamp,
            'open_price': data.open_price,
            'high_price': data.high_price,
            'low_price': data.low_price,
            'close_price': data.close_price,
            'volume': data.volume
        } for data in market_data])
        
        technical_signals = signal_generator._calculate_technical_signals(df)
        
        # Calculate individual indicator strengths
        indicator_breakdown = {
            "rsi": {
                "signal": technical_signals.get('rsi_signal', 'HOLD'),
                "strength": technical_signals.get('rsi_strength', 0.0),
                "weight": 0.2
            },
            "macd": {
                "signal": technical_signals.get('macd_signal', 'HOLD'),
                "strength": technical_signals.get('macd_strength', 0.0),
                "weight": 0.25
            },
            "moving_averages": {
                "signal": technical_signals.get('ma_signal', 'HOLD'),
                "strength": technical_signals.get('ma_strength', 0.0),
                "weight": 0.2
            },
            "bollinger_bands": {
                "signal": technical_signals.get('bb_signal', 'HOLD'),
                "strength": technical_signals.get('bb_strength', 0.0),
                "weight": 0.15
            },
            "volume": {
                "confirmation": technical_signals.get('volume_confirmation', False),
                "strength": technical_signals.get('volume_strength', 0.0),
                "weight": 0.1
            }
        }
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "overall_signal": {
                "type": latest_signal.signal_type,
                "strength": latest_signal.strength,
                "reasoning": latest_signal.reasoning
            },
            "indicator_breakdown": indicator_breakdown,
            "price_targets": {
                "target": latest_signal.price_target,
                "stop_loss": latest_signal.stop_loss,
                "support": latest_signal.support_level,
                "resistance": latest_signal.resistance_level
            },
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get signal strength breakdown: {str(e)}"
        )