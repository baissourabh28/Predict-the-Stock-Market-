"""
ML Predictions API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.market_data import PredictionRequest, PredictionResponse, PredictionSchema
from app.services.data_service import DataService
from app.services.ml_service import PredictionEngine
from app.services.cache_service import MarketDataCache
from app.models.user import User

router = APIRouter(prefix="/predictions", tags=["ML Predictions"])

# Initialize services
data_service = DataService()
prediction_engine = PredictionEngine()
cache_service = MarketDataCache()


@router.on_event("startup")
async def startup_prediction_service():
    """Initialize prediction service on startup"""
    await data_service.initialize()


@router.post("/generate", response_model=Dict[str, Any])
async def generate_prediction(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate ML prediction for a symbol"""
    try:
        # Check cache first
        cached_prediction = cache_service.get_prediction(
            request.symbol, request.timeframe, request.time_horizon
        )
        if cached_prediction:
            return {
                "symbol": request.symbol,
                "timeframe": request.timeframe,
                "time_horizon": request.time_horizon,
                "prediction": cached_prediction,
                "source": "cache",
                "timestamp": datetime.now()
            }
        
        # Get market data for prediction
        market_data = data_service.get_market_data(
            db, request.symbol, request.timeframe, limit=300
        )
        
        if len(market_data) < 60:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient data for prediction. Need at least 60 records, got {len(market_data)}"
            )
        
        # Generate prediction
        prediction_result = prediction_engine.generate_prediction(
            market_data, request.symbol, request.timeframe, request.time_horizon
        )
        
        # Store prediction in database
        prediction_schema = PredictionSchema(
            symbol=request.symbol,
            predicted_price=prediction_result['predicted_price'],
            confidence_score=prediction_result['confidence_score'],
            time_horizon=request.time_horizon,
            timeframe=request.timeframe,
            model_used="ensemble"
        )
        
        stored_prediction = data_service.store_prediction(db, prediction_schema)
        
        # Cache the prediction
        cache_service.cache_prediction(
            request.symbol, request.timeframe, request.time_horizon, 
            prediction_result, ttl=600
        )
        
        return {
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "time_horizon": request.time_horizon,
            "prediction": prediction_result,
            "source": "generated",
            "prediction_id": stored_prediction.id,
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate prediction: {str(e)}"
        )


@router.get("/history/{symbol}", response_model=List[PredictionResponse])
async def get_prediction_history(
    symbol: str,
    timeframe: str = "1D",
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get prediction history for a symbol"""
    try:
        predictions = data_service.get_predictions(db, symbol, timeframe, limit)
        return predictions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get prediction history: {str(e)}"
        )


@router.get("/performance/{symbol}")
async def get_model_performance(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get model performance statistics for a symbol"""
    try:
        performance_stats = prediction_engine.get_model_performance_stats(symbol)
        
        return {
            "symbol": symbol,
            "performance_stats": performance_stats,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model performance: {str(e)}"
        )


@router.post("/train/{symbol}")
async def train_models(
    symbol: str,
    background_tasks: BackgroundTasks,
    days: int = 365,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Train ML models for a symbol (background task)"""
    try:
        # Get historical data for training
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        historical_data = data_service.get_historical_data(
            db, symbol, start_date, end_date, "1D"
        )
        
        if len(historical_data) < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient data for training. Need at least 100 records, got {len(historical_data)}"
            )
        
        # Add background task for model training
        background_tasks.add_task(
            prediction_engine.model_manager.train_models,
            historical_data, symbol
        )
        
        return {
            "message": f"Model training initiated for {symbol}",
            "symbol": symbol,
            "training_data_points": len(historical_data),
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate model training: {str(e)}"
        )


@router.post("/update-performance/{symbol}")
async def update_model_performance(
    symbol: str,
    actual_price: float,
    predicted_price: float,
    model_name: str = "ensemble",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update model performance with actual vs predicted prices"""
    try:
        prediction_engine.update_model_performance(
            symbol, actual_price, predicted_price, model_name
        )
        
        return {
            "message": "Model performance updated successfully",
            "symbol": symbol,
            "model_name": model_name,
            "actual_price": actual_price,
            "predicted_price": predicted_price,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update model performance: {str(e)}"
        )


@router.get("/confidence-analysis/{symbol}")
async def get_confidence_analysis(
    symbol: str,
    timeframe: str = "1D",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get confidence analysis for predictions"""
    try:
        # Get recent predictions
        recent_predictions = data_service.get_predictions(db, symbol, timeframe, limit=20)
        
        if not recent_predictions:
            return {
                "symbol": symbol,
                "message": "No predictions available for confidence analysis",
                "timestamp": datetime.now()
            }
        
        # Calculate confidence statistics
        confidence_scores = [pred.confidence_score for pred in recent_predictions]
        
        analysis = {
            "symbol": symbol,
            "timeframe": timeframe,
            "total_predictions": len(recent_predictions),
            "avg_confidence": round(sum(confidence_scores) / len(confidence_scores), 3),
            "min_confidence": round(min(confidence_scores), 3),
            "max_confidence": round(max(confidence_scores), 3),
            "confidence_trend": "improving" if len(confidence_scores) > 5 and 
                              confidence_scores[-5:] > confidence_scores[:5] else "stable",
            "recent_predictions": [
                {
                    "predicted_price": pred.predicted_price,
                    "confidence_score": pred.confidence_score,
                    "time_horizon": pred.time_horizon,
                    "created_at": pred.created_at
                } for pred in recent_predictions[:5]
            ],
            "timestamp": datetime.now()
        }
        
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get confidence analysis: {str(e)}"
        )