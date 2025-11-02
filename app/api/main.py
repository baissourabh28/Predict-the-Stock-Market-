"""
Main API router that includes all endpoint routers
"""
from fastapi import APIRouter
from app.api.routers import auth, market_data, predictions, signals

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(market_data.router)
api_router.include_router(predictions.router)
api_router.include_router(signals.router)

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "service": "Trading Dashboard API",
        "version": "1.0.0"
    }