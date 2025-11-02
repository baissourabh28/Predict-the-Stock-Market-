# 📈 AI-Powered Trading Dashboard

A comprehensive, real-time trading dashboard built with **FastAPI** (Python) backend and **React TypeScript** frontend. Features AI/ML-powered price predictions, technical analysis, and interactive candlestick charts.

![Trading Dashboard](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![React](https://img.shields.io/badge/React-18+-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688)

## 🚀 Features

### 📊 **Interactive Trading Interface**
- **Real-time Candlestick Charts** with custom canvas rendering
- **Multiple Timeframes** (1m, 5m, 15m, 1H, 1D, 1W)
- **Stock Search & Selection** with popular Indian stocks
- **Live Market Data** simulation with realistic price movements

### 🤖 **AI/ML Powered Analytics**
- **Price Predictions** using ensemble ML models (LSTM, Random Forest, SVR)
- **Trading Signal Generation** with BUY/SELL/HOLD recommendations
- **Technical Indicators** (RSI, MACD, Moving Averages, Bollinger Bands)
- **Confidence Scoring** for all predictions and signals

### 🎨 **Modern UI/UX**
- **Glassmorphism Design** with smooth animations
- **Responsive Layout** for desktop and mobile
- **Dark Theme** optimized for trading
- **Real-time Updates** with WebSocket support

### 🔐 **Security & Authentication**
- **JWT-based Authentication** with secure token management
- **Protected Routes** and role-based access
- **Input Validation** and SQL injection prevention
- **Rate Limiting** and API security

## 🛠️ Technology Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - Database ORM with Alembic migrations
- **JWT Authentication** - Secure token-based auth
- **scikit-learn & TensorFlow** - Machine learning models
- **Redis** - Caching and session management
- **SQLite** - Database (easily switchable to PostgreSQL)

### Frontend
- **React 18** with TypeScript
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Chart.js** - Interactive charts and visualizations
- **CSS3** - Modern styling with animations

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### 🚀 Quick Start (One Command)

```bash
# Clone the repository
git clone https://github.com/yourusername/trading-dashboard.git
cd trading-dashboard

# Run the complete setup
python start_trading_dashboard.py
```

This single command will:
- ✅ Install Python dependencies
- ✅ Set up the database
- ✅ Install frontend dependencies  
- ✅ Start both backend and frontend servers
- ✅ Create a test user account
- ✅ Open the dashboard in your browser

### 🔧 Manual Setup

#### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Create test user
python create_user.py

# Start backend server
python main.py
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 🔑 Default Login Credentials
- **Username**: `testuser`
- **Password**: `testpassword123`

## 📁 Project Structure

```
trading-dashboard/
├── app/                          # Backend application
│   ├── api/                      # API routes
│   │   └── routers/             # Individual route modules
│   ├── core/                    # Core functionality
│   │   ├── config.py           # Configuration settings
│   │   ├── database.py         # Database setup
│   │   └── security.py         # Authentication logic
│   ├── models/                  # Database models
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic
│   │   ├── auth_service.py     # Authentication service
│   │   ├── data_service.py     # Market data service
│   │   ├── ml_service.py       # ML prediction service
│   │   └── signal_service.py   # Trading signals
│   └── ml/                      # Machine learning models
├── frontend/                     # React frontend
│   ├── public/                  # Static files
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── contexts/            # React contexts
│   │   ├── pages/               # Page components
│   │   └── styles/              # CSS stylesheets
│   └── package.json
├── alembic/                     # Database migrations
├── main.py                      # FastAPI application entry
├── requirements.txt             # Python dependencies
└── README.md
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=sqlite:///./trading_dashboard.db

# JWT Settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=Trading Dashboard

# External APIs (Optional)
UPSTOX_API_KEY=your-upstox-api-key
UPSTOX_SECRET=your-upstox-secret
```

## 🤖 Machine Learning Models

The system includes multiple ML models for price prediction:

### 1. **LSTM Neural Network**
- **Purpose**: Time series forecasting
- **Features**: Sequential price data, volume, technical indicators
- **Output**: Next period price prediction

### 2. **Random Forest Regressor**
- **Purpose**: Pattern recognition in market data
- **Features**: Technical indicators, market sentiment
- **Output**: Price direction and magnitude

### 3. **Support Vector Regression**
- **Purpose**: Non-linear price trend analysis
- **Features**: Normalized price data, volatility metrics
- **Output**: Support/resistance levels

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user

### Market Data
- `GET /api/v1/market-data/live/{symbol}` - Live market data
- `POST /api/v1/market-data/historical` - Historical data
- `GET /api/v1/market-data/symbols` - Available symbols

### Predictions & Signals
- `POST /api/v1/predictions/generate` - Generate ML predictions
- `POST /api/v1/signals/generate` - Generate trading signals
- `GET /api/v1/signals/technical-analysis/{symbol}` - Technical indicators

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Production Deployment
```bash
# Backend (using Gunicorn)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend (build for production)
cd frontend
npm run build
```

## 🧪 Testing

```bash
# Run backend tests
pytest

# Run frontend tests
cd frontend
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent Python web framework
- **React** team for the powerful frontend library
- **scikit-learn** for machine learning capabilities
- **Chart.js** for beautiful chart visualizations

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/trading-dashboard/issues) page
2. Create a new issue with detailed information
3. Join our community discussions

---

**⭐ Star this repository if you find it helpful!**

Made with ❤️ for the trading community