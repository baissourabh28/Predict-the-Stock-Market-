# Backend Documentation

## Overview
FastAPI backend for AI-powered trading dashboard with real-time market data, ML predictions, and trading signals.

## Tech Stack
- FastAPI 0.104.1
- SQLAlchemy 2.0.23 (ORM)
- PostgreSQL/SQLite (Database)
- Redis (Caching - optional)
- TensorFlow 2.15.0 (ML)
- yfinance (Market Data)
- bcrypt (Password Hashing)
- JWT (Authentication)

## Project Structure
```
app/
├── api/
│   ├── main.py              # FastAPI app initialization
│   └── routers/             # API route handlers
│       ├── auth.py          # Authentication endpoints
│       ├── market_data.py   # Market data endpoints
│       ├── predictions.py   # ML prediction endpoints
│       └── signals.py       # Trading signal endpoints
├── core/
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── dependencies.py      # Dependency injection
│   ├── middleware.py        # Custom middleware
│   ├── security.py          # Security utilities
│   └── validators.py        # Input validation
├── models/
│   ├── user.py              # User database model
│   └── market_data.py       # Market data models
├── schemas/
│   ├── user.py              # User Pydantic schemas
│   └── market_data.py       # Market data schemas
├── services/
│   ├── auth_service.py      # Authentication logic
│   ├── cache_service.py     # Redis caching
│   ├── data_service.py      # Data management
│   ├── ml_service.py        # ML predictions
│   ├── signal_service.py    # Trading signals
│   ├── yahoo_finance_service.py  # Real market data
│   └── upstox_service.py    # Legacy (not used)
└── ml/
    ├── models.py            # ML model definitions
    └── feature_engineering.py  # Feature extraction
```

## Database Models

### User
```python
- id: Integer (Primary Key)
- username: String (Unique)
- email: String (Unique)
- hashed_password: String
- is_active: Boolean
- created_at: DateTime
```

### MarketData
```python
- id: Integer (Primary Key)
- symbol: String
- timestamp: DateTime
- open_price: Float
- high_price: Float
- low_price: Float
- close_price: Float
- volume: Integer
- timeframe: String
```

### Prediction
```python
- id: Integer (Primary Key)
- symbol: String
- predicted_price: Float
- confidence_score: Float
- time_horizon: String
- timeframe: String
- model_used: String
- created_at: DateTime
```

### TradingSignal
```python
- id: Integer (Primary Key)
- symbol: String
- signal_type: String (BUY/SELL/HOLD)
- strength: Float
- price_target: Float
- stop_loss: Float
- support_level: Float
- resistance_level: Float
- timeframe: String
- reasoning: String
- created_at: DateTime
```

## Configuration

### Environment Variables (.env)
```env
# Database
DATABASE_URL=sqlite:///./trading_dashboard.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# API Keys (if needed)
# UPSTOX_API_KEY=your-key
# UPSTOX_API_SECRET=your-secret
```

### Config Management
All configuration in `app/core/config.py` using Pydantic Settings:
```python
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
```

## Security Features

### Password Hashing
- bcrypt with salt rounds
- No fallback to weak algorithms
- Secure password verification

### JWT Authentication
- Token-based authentication
- Configurable expiration
- Secure token generation

### Input Validation
- Pydantic schemas for all inputs
- Custom validators for symbols, timeframes
- SQL injection prevention

### CORS Configuration
```python
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]
```

## Real Market Data Integration

### Yahoo Finance Service
Free, no API key required:

```python
# Supported symbols
RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS
ICICIBANK.NS, SBIN.NS, BHARTIARTL.NS
^NSEI (NIFTY50), ^BSESN (SENSEX)
```

### Features
- Real-time quotes
- Historical data (years of data)
- Multiple timeframes (1m, 5m, 15m, 1H, 1D, 1W)
- Volume data
- Market status detection

### Usage
```python
from app.services.yahoo_finance_service import YahooFinanceService

service = YahooFinanceService()
quote = await service.get_live_quote('RELIANCE', '1m')
historical = await service.get_historical_candles('TCS', days=30, timeframe='1D')
```

## ML Models

### LSTM (Long Short-Term Memory)
- Time series prediction
- Sequence learning
- Best for trend following

### Random Forest
- Ensemble learning
- Feature importance
- Robust to overfitting

### SVR (Support Vector Regression)
- Non-linear relationships
- Kernel-based learning
- Good for complex patterns

### Feature Engineering
- Technical indicators (RSI, MACD, Bollinger Bands)
- Price momentum
- Volume analysis
- Moving averages

## API Endpoints

### Authentication
```
POST /api/auth/register    - Register new user
POST /api/auth/login       - Login user
GET  /api/auth/me          - Get current user
```

### Market Data
```
GET  /api/market/quote/{symbol}           - Live quote
GET  /api/market/historical/{symbol}      - Historical data
POST /api/market/sync/{symbol}            - Sync data
GET  /api/market/multiple                 - Multiple quotes
```

### Predictions
```
GET  /api/predictions/{symbol}            - Get predictions
POST /api/predictions/generate/{symbol}   - Generate prediction
```

### Trading Signals
```
GET  /api/signals/{symbol}                - Get signals
POST /api/signals/generate/{symbol}       - Generate signal
```

### Health Check
```
GET  /health                              - System health
```

## Database Migrations

Using Alembic:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Caching Strategy

### Redis (Optional)
- Market data caching (5 min TTL)
- Prediction caching (15 min TTL)
- Signal caching (10 min TTL)
- Graceful degradation if Redis unavailable

## Error Handling

### Global Exception Handler
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### Logging
Structured logging with structlog:
```python
logger.info("Event occurred", key="value")
logger.error("Error occurred", error=str(e))
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Create test user
python create_user.py
```

## Development

```bash
# Run server
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server runs on http://localhost:8000

## Testing

```bash
# Test API connection
python test_api_connection.py

# Reset test user
python reset_test_user.py
```

## Production Deployment

### Requirements
- Python 3.9+
- PostgreSQL (recommended)
- Redis (optional)
- 2GB RAM minimum

### Steps
1. Set production environment variables
2. Use PostgreSQL instead of SQLite
3. Enable Redis for caching
4. Configure HTTPS
5. Set strong SECRET_KEY
6. Use production ASGI server (Gunicorn + Uvicorn)

### Production Command
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Performance Optimization

1. **Database Indexing**: Indexes on symbol, timestamp
2. **Connection Pooling**: SQLAlchemy pool configuration
3. **Caching**: Redis for frequently accessed data
4. **Async Operations**: FastAPI async endpoints
5. **Query Optimization**: Limit results, use pagination

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
Structured JSON logs for easy parsing and monitoring.

### Metrics
- Request count
- Response time
- Error rate
- Database connections

## Security Best Practices

1. **Never commit .env files**
2. **Use strong SECRET_KEY in production**
3. **Enable HTTPS in production**
4. **Validate all inputs**
5. **Rate limiting on auth endpoints**
6. **Regular security updates**

## Troubleshooting

### Database Connection Issues
Check DATABASE_URL in .env file

### Redis Connection Issues
Redis is optional - app works without it

### Import Errors
Ensure all dependencies installed: `pip install -r requirements.txt`

### Migration Issues
Reset database: `alembic downgrade base && alembic upgrade head`

## API Documentation

Interactive docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
