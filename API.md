# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <token>
```

---

## Authentication Endpoints

### Register User
```http
POST /api/auth/register
```

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

### Login
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Get Current User
```http
GET /api/auth/me
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

---

## Market Data Endpoints

### Get Live Quote
```http
GET /api/market/quote/{symbol}?timeframe=1m
```

**Parameters:**
- `symbol` (path): Stock symbol (e.g., RELIANCE, TCS, INFY)
- `timeframe` (query): 1m, 5m, 15m, 1H, 1D, 1W (default: 1m)

**Response:** `200 OK`
```json
{
  "symbol": "RELIANCE",
  "timestamp": "2024-01-01T10:30:00",
  "open_price": 1420.50,
  "high_price": 1425.00,
  "low_price": 1418.00,
  "close_price": 1423.00,
  "volume": 1500000,
  "timeframe": "1m"
}
```

### Get Historical Data
```http
GET /api/market/historical/{symbol}?start_date=2024-01-01&end_date=2024-01-31&timeframe=1D
```

**Parameters:**
- `symbol` (path): Stock symbol
- `start_date` (query): Start date (YYYY-MM-DD)
- `end_date` (query): End date (YYYY-MM-DD)
- `timeframe` (query): 1m, 5m, 15m, 1H, 1D, 1W

**Response:** `200 OK`
```json
[
  {
    "symbol": "RELIANCE",
    "timestamp": "2024-01-01T09:15:00",
    "open_price": 1400.00,
    "high_price": 1425.00,
    "low_price": 1395.00,
    "close_price": 1420.00,
    "volume": 5000000,
    "timeframe": "1D"
  }
]
```

### Sync Market Data
```http
POST /api/market/sync/{symbol}?days=30&timeframe=1D
```

**Parameters:**
- `symbol` (path): Stock symbol
- `days` (query): Number of days (default: 30)
- `timeframe` (query): Timeframe (default: 1D)

**Response:** `200 OK`
```json
{
  "message": "Synced 30 records for RELIANCE",
  "records": 30
}
```

### Get Multiple Quotes
```http
GET /api/market/multiple?symbols=RELIANCE,TCS,INFY&timeframe=1m
```

**Parameters:**
- `symbols` (query): Comma-separated symbols
- `timeframe` (query): Timeframe (default: 1m)

**Response:** `200 OK`
```json
{
  "RELIANCE": {
    "symbol": "RELIANCE",
    "close_price": 1423.00,
    "timestamp": "2024-01-01T10:30:00"
  },
  "TCS": {
    "symbol": "TCS",
    "close_price": 3450.00,
    "timestamp": "2024-01-01T10:30:00"
  }
}
```

### Get Market Status
```http
GET /api/market/status
```

**Response:** `200 OK`
```json
{
  "status": "OPEN",
  "message": "Market is open",
  "timestamp": "2024-01-01T10:30:00"
}
```

---

## Prediction Endpoints

### Get Predictions
```http
GET /api/predictions/{symbol}?timeframe=1D&limit=10
```

**Parameters:**
- `symbol` (path): Stock symbol
- `timeframe` (query): Timeframe (default: 1D)
- `limit` (query): Number of predictions (default: 10)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "symbol": "RELIANCE",
    "predicted_price": 1450.00,
    "confidence_score": 0.85,
    "time_horizon": "1D",
    "timeframe": "1D",
    "model_used": "LSTM",
    "created_at": "2024-01-01T10:00:00"
  }
]
```

### Generate Prediction
```http
POST /api/predictions/generate/{symbol}?timeframe=1D&model=LSTM
```

**Parameters:**
- `symbol` (path): Stock symbol
- `timeframe` (query): Timeframe (default: 1D)
- `model` (query): LSTM, RandomForest, SVR (default: LSTM)

**Response:** `201 Created`
```json
{
  "symbol": "RELIANCE",
  "predicted_price": 1450.00,
  "confidence_score": 0.85,
  "time_horizon": "1D",
  "timeframe": "1D",
  "model_used": "LSTM",
  "created_at": "2024-01-01T10:00:00"
}
```

---

## Trading Signal Endpoints

### Get Trading Signals
```http
GET /api/signals/{symbol}?timeframe=1D&limit=10
```

**Parameters:**
- `symbol` (path): Stock symbol
- `timeframe` (query): Timeframe (default: 1D)
- `limit` (query): Number of signals (default: 10)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "symbol": "RELIANCE",
    "signal_type": "BUY",
    "strength": 0.75,
    "price_target": 1500.00,
    "stop_loss": 1380.00,
    "support_level": 1400.00,
    "resistance_level": 1480.00,
    "timeframe": "1D",
    "reasoning": "Strong uptrend with RSI oversold",
    "created_at": "2024-01-01T10:00:00"
  }
]
```

### Generate Trading Signal
```http
POST /api/signals/generate/{symbol}?timeframe=1D
```

**Parameters:**
- `symbol` (path): Stock symbol
- `timeframe` (query): Timeframe (default: 1D)

**Response:** `201 Created`
```json
{
  "symbol": "RELIANCE",
  "signal_type": "BUY",
  "strength": 0.75,
  "price_target": 1500.00,
  "stop_loss": 1380.00,
  "support_level": 1400.00,
  "resistance_level": 1480.00,
  "timeframe": "1D",
  "reasoning": "Strong uptrend with RSI oversold",
  "created_at": "2024-01-01T10:00:00"
}
```

---

## Health Check

### System Health
```http
GET /health
```

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2024-01-01T10:00:00"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid symbol format"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Supported Symbols

### Indian Stocks (NSE)
```
RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK
SBIN, BHARTIARTL, ITC, HINDUNILVR, KOTAKBANK
LT, ASIANPAINTS, MARUTI, HCLTECH, AXISBANK
ULTRACEMCO, SUNPHARMA, TITAN, WIPRO, TECHM
POWERGRID, NTPC, ONGC, COALINDIA, TATAMOTORS
TATASTEEL, JSWSTEEL, HINDALCO
```

### Indices
```
NIFTY50 (^NSEI)
SENSEX (^BSESN)
```

---

## Rate Limits

- Authentication: 5 requests/minute
- Market Data: 60 requests/minute
- Predictions: 10 requests/minute
- Signals: 10 requests/minute

---

## Timeframes

- `1m` - 1 minute
- `5m` - 5 minutes
- `15m` - 15 minutes
- `1H` - 1 hour
- `1D` - 1 day
- `1W` - 1 week

---

## Signal Types

- `BUY` - Buy recommendation
- `SELL` - Sell recommendation
- `HOLD` - Hold position

---

## ML Models

- `LSTM` - Long Short-Term Memory
- `RandomForest` - Random Forest Regressor
- `SVR` - Support Vector Regression

---

## Interactive Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Example Usage

### Python
```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"username": "testuser", "password": "testpassword123"}
)
token = response.json()["access_token"]

# Get quote
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/market/quote/RELIANCE?timeframe=1m",
    headers=headers
)
quote = response.json()
print(f"RELIANCE: ₹{quote['close_price']}")
```

### JavaScript
```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'testuser', password: 'testpassword123' })
});
const { access_token } = await loginResponse.json();

// Get quote
const quoteResponse = await fetch(
  'http://localhost:8000/api/market/quote/RELIANCE?timeframe=1m',
  { headers: { 'Authorization': `Bearer ${access_token}` } }
);
const quote = await quoteResponse.json();
console.log(`RELIANCE: ₹${quote.close_price}`);
```

### cURL
```bash
# Login
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpassword123"}' \
  | jq -r '.access_token')

# Get quote
curl "http://localhost:8000/api/market/quote/RELIANCE?timeframe=1m" \
  -H "Authorization: Bearer $TOKEN"
```
