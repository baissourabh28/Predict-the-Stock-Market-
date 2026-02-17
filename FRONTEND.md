# Frontend Documentation

## Overview
React TypeScript frontend for AI-powered trading dashboard with real-time charts, ML predictions, and paper trading.

## Tech Stack
- React 18.2.0 with TypeScript
- React Router for navigation
- Chart.js for data visualization
- Axios for API communication
- TailwindCSS for styling

## Project Structure
```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── EnhancedTradingDashboard.tsx
│   │   ├── ErrorBoundary.tsx
│   │   ├── Navbar.tsx
│   │   ├── PaperTradingPanel.tsx
│   │   ├── ProtectedRoute.tsx
│   │   └── TradingViewChart.tsx
│   ├── pages/              # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   └── Settings.tsx
│   ├── contexts/           # React contexts
│   │   └── AuthContext.tsx
│   ├── services/           # API services
│   │   └── MarketDataService.ts
│   ├── config/             # Configuration
│   │   └── api.ts
│   ├── utils/              # Utility functions
│   │   └── storage.ts
│   └── styles/             # CSS files
│       ├── colors.css
│       ├── Dashboard.css
│       ├── EnhancedTradingDashboard.css
│       ├── Navbar.css
│       ├── PaperTrading.css
│       ├── Settings.css
│       └── TradingViewChart.css
├── public/
│   └── index.html
├── package.json
└── tsconfig.json
```

## Color Scheme
Professional blue-purple theme for financial applications:

### Primary Colors
- Primary: `#4F46E5` (Indigo)
- Primary Light: `#6366F1`
- Primary Dark: `#4338CA`
- Gradient: `linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)`

### Accent Colors
- Accent: `#F59E0B` (Gold)
- Accent Light: `#FBBF24`
- Accent Dark: `#D97706`

### Status Colors
- Success: `#10B981` (Green) - Profits, BUY signals
- Danger: `#EF4444` (Red) - Losses, SELL signals

### Dark Theme
- Background Primary: `#0f1419`
- Background Secondary: `#1a1f2e`
- Background Tertiary: `#2d3748`
- Text Primary: `#ffffff`
- Text Secondary: `#a0aec0`

## Key Features

### 1. Authentication
- JWT-based authentication
- Protected routes
- Persistent login with localStorage
- Auto-redirect on auth failure

### 2. Real-Time Trading Dashboard
- Live stock price updates
- Multiple timeframe support (1m, 5m, 15m, 1H, 1D, 1W)
- Interactive candlestick charts
- Volume indicators
- Technical analysis overlays

### 3. ML Predictions
- LSTM, Random Forest, SVR models
- Confidence scores
- Time horizon predictions
- Visual confidence indicators

### 4. Trading Signals
- BUY/SELL/HOLD recommendations
- Signal strength indicators
- Price targets and stop losses
- Support/resistance levels

### 5. Paper Trading
- Virtual portfolio management
- Buy/sell simulation
- P&L tracking
- Position management

### 6. Error Handling
- Global error boundary
- Safe localStorage wrapper
- API error handling
- User-friendly error messages

## Environment Configuration

Create `.env` file:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## Installation

```bash
cd frontend
npm install
```

## Development

```bash
npm start
```
Runs on http://localhost:3000

## Build

```bash
npm run build
```
Creates optimized production build in `build/` directory

## Key Components

### EnhancedTradingDashboard
Main trading interface with charts, signals, and predictions.

### ErrorBoundary
Catches React errors and displays fallback UI.

### PaperTradingPanel
Virtual trading interface for practice trading.

### TradingViewChart
Candlestick chart component with technical indicators.

### AuthContext
Manages authentication state across the application.

## API Integration

### MarketDataService
Handles all API calls to backend:
- `getMarketData()` - Fetch historical data
- `getLiveQuote()` - Get real-time quotes
- `getPredictions()` - Fetch ML predictions
- `getTradingSignals()` - Get trading signals

### API Configuration
Centralized in `config/api.ts`:
```typescript
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

## Storage Utilities

Safe localStorage wrapper with error handling:
```typescript
import { storage } from './utils/storage';

storage.setItem('key', 'value');
const value = storage.getItem('key');
storage.removeItem('key');
storage.clear();
```

## Styling

### CSS Variables
All colors defined in `styles/colors.css` using CSS custom properties.

### Component Styles
Each major component has its own CSS file for maintainability.

### Responsive Design
Mobile-first approach with breakpoints at 768px.

## Best Practices

1. **Type Safety**: Full TypeScript coverage
2. **Error Handling**: Try-catch blocks with user feedback
3. **Code Splitting**: Lazy loading for routes
4. **Performance**: Memoization and optimization
5. **Accessibility**: ARIA labels and semantic HTML

## Testing

```bash
npm test
```

## Troubleshooting

### CORS Issues
Ensure backend CORS is configured for http://localhost:3000

### API Connection
Check `REACT_APP_API_URL` in `.env` file

### Build Errors
Clear cache: `rm -rf node_modules package-lock.json && npm install`

## Production Deployment

1. Update `.env` with production API URL
2. Build: `npm run build`
3. Serve `build/` directory with web server
4. Configure HTTPS and domain

## Browser Support
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
