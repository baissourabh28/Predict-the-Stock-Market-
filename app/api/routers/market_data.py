"""
Market data API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.market_data import (
    MarketDataRequest, MarketDataResponse, HistoricalDataRequest,
    MultipleSymbolsRequest, CandlestickDataSchema
)
from app.services.data_service import DataService
from app.services.cache_service import MarketDataCache
from app.models.user import User

router = APIRouter(prefix="/market-data", tags=["Market Data"])


# Initialize services
data_service = DataService()
cache_service = MarketDataCache()


@router.on_event("startup")
async def startup_market_data_service():
    """Initialize data service on startup"""
    await data_service.initialize()


@router.on_event("shutdown")
async def shutdown_market_data_service():
    """Cleanup data service on shutdown"""
    await data_service.cleanup()


@router.get("/live/{symbol}", response_model=Dict[str, Any])
async def get_live_data(
    symbol: str,
    timeframe: str = "1m",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get live market data for a symbol"""
    try:
        # Check cache first
        cached_data = cache_service.get_live_data(symbol, timeframe)
        if cached_data:
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "data": cached_data,
                "source": "cache",
                "timestamp": datetime.now()
            }
        
        # Fetch from API and store
        market_data = await data_service.fetch_and_store_live_data(db, symbol, timeframe)
        
        if not market_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No live data available for symbol {symbol}"
            )
        
        # Convert to dict for caching
        data_dict = {
            "id": market_data.id,
            "symbol": market_data.symbol,
            "timestamp": market_data.timestamp.isoformat(),
            "open_price": market_data.open_price,
            "high_price": market_data.high_price,
            "low_price": market_data.low_price,
            "close_price": market_data.close_price,
            "volume": market_data.volume,
            "timeframe": market_data.timeframe
        }
        
        # Cache the data
        cache_service.cache_live_data(symbol, timeframe, data_dict, ttl=60)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": data_dict,
            "source": "api",
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch live data: {str(e)}"
        )


@router.post("/historical", response_model=Dict[str, Any])
async def get_historical_data(
    request: HistoricalDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get historical market data"""
    try:
        # Calculate days for caching
        days = (request.end_date - request.start_date).days
        
        # Check cache first
        cached_data = cache_service.get_historical_data(request.symbol, request.timeframe, days)
        if cached_data:
            return {
                "symbol": request.symbol,
                "timeframe": request.timeframe,
                "start_date": request.start_date,
                "end_date": request.end_date,
                "data": cached_data,
                "source": "cache",
                "count": len(cached_data)
            }
        
        # Fetch from database first
        historical_data = data_service.get_historical_data(
            db, request.symbol, request.start_date, request.end_date, request.timeframe
        )
        
        # If not enough data in DB, fetch from API
        if len(historical_data) < days * 0.8:  # Less than 80% of expected data
            historical_data = await data_service.fetch_and_store_historical_data(
                db, request.symbol, days, request.timeframe
            )
        
        if not historical_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No historical data available for symbol {request.symbol}"
            )
        
        # Convert to dict list
        data_list = [{
            "id": data.id,
            "symbol": data.symbol,
            "timestamp": data.timestamp.isoformat(),
            "open_price": data.open_price,
            "high_price": data.high_price,
            "low_price": data.low_price,
            "close_price": data.close_price,
            "volume": data.volume,
            "timeframe": data.timeframe
        } for data in historical_data]
        
        # Cache the data
        cache_service.cache_historical_data(request.symbol, request.timeframe, days, data_list)
        
        return {
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "data": data_list,
            "source": "database",
            "count": len(data_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch historical data: {str(e)}"
        )


@router.post("/multiple-quotes", response_model=Dict[str, Any])
async def get_multiple_quotes(
    request: MultipleSymbolsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get live quotes for multiple symbols"""
    try:
        quotes = await data_service.get_multiple_live_quotes(
            db, request.symbols, request.timeframe
        )
        
        # Convert to response format
        result = {}
        for symbol, market_data in quotes.items():
            result[symbol] = {
                "id": market_data.id,
                "symbol": market_data.symbol,
                "timestamp": market_data.timestamp.isoformat(),
                "open_price": market_data.open_price,
                "high_price": market_data.high_price,
                "low_price": market_data.low_price,
                "close_price": market_data.close_price,
                "volume": market_data.volume,
                "timeframe": market_data.timeframe
            }
        
        return {
            "timeframe": request.timeframe,
            "quotes": result,
            "timestamp": datetime.now(),
            "count": len(result)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch multiple quotes: {str(e)}"
        )


@router.get("/latest-price/{symbol}")
async def get_latest_price(
    symbol: str,
    timeframe: str = "1m",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the latest price for a symbol"""
    try:
        latest_price = data_service.get_latest_price(db, symbol, timeframe)
        
        if latest_price is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No price data available for symbol {symbol}"
            )
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "latest_price": latest_price,
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get latest price: {str(e)}"
        )


@router.post("/refresh/{symbol}")
async def refresh_market_data(
    symbol: str,
    background_tasks: BackgroundTasks,
    timeframe: str = "1m",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Refresh market data for a symbol (background task)"""
    try:
        # Invalidate cache
        cache_service.invalidate_symbol_cache(symbol)
        
        # Add background task to fetch fresh data
        background_tasks.add_task(
            data_service.fetch_and_store_live_data,
            db, symbol, timeframe
        )
        
        return {
            "message": f"Market data refresh initiated for {symbol}",
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh market data: {str(e)}"
        )


@router.get("/cache-stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user)
):
    """Get cache statistics"""
    try:
        stats = cache_service.get_cache_stats()
        return {
            "cache_stats": stats,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache stats: {str(e)}"
        )