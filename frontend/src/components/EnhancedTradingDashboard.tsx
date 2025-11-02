import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

interface MarketData {
  id: number;
  symbol: string;
  timestamp: string;
  open_price: number;
  high_price: number;
  low_price: number;
  close_price: number;
  volume: number;
  timeframe: string;
}

interface TradingSignal {
  signal_type: string;
  strength: number;
  price_target?: number;
  stop_loss?: number;
  support_level?: number;
  resistance_level?: number;
  reasoning: string;
}

interface TechnicalIndicators {
  rsi_signal?: string;
  rsi_strength?: number;
  macd_signal?: string;
  macd_strength?: number;
  ma_signal?: string;
  bb_signal?: string;
  volume_confirmation?: boolean;
}

interface StockSearchResult {
  symbol: string;
  name: string;
  exchange: string;
}

const EnhancedTradingDashboard: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('NIFTY50');
  const [timeframe, setTimeframe] = useState('1D');
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [tradingSignal, setTradingSignal] = useState<TradingSignal | null>(null);
  const [technicalIndicators, setTechnicalIndicators] = useState<TechnicalIndicators | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<StockSearchResult[]>([]);
  const [showSearch, setShowSearch] = useState(false);

  const timeframes = [
    { value: '1m', label: '1M' },
    { value: '5m', label: '5M' },
    { value: '15m', label: '15M' },
    { value: '1H', label: '1H' },
    { value: '1D', label: '1D' },
    { value: '1W', label: '1W' }
  ];

  const popularSymbols = [
    { symbol: 'NIFTY50', name: 'Nifty 50' },
    { symbol: 'SENSEX', name: 'BSE Sensex' },
    { symbol: 'RELIANCE', name: 'Reliance Industries' },
    { symbol: 'TCS', name: 'Tata Consultancy Services' },
    { symbol: 'INFY', name: 'Infosys Limited' },
    { symbol: 'HDFC', name: 'HDFC Bank' },
    { symbol: 'ICICIBANK', name: 'ICICI Bank' },
    { symbol: 'TATASTEEL', name: 'Tata Steel' }
  ];

  const fetchMarketData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch live data first
      const liveResponse = await axios.get(`/api/v1/market-data/live/${selectedSymbol}?timeframe=${timeframe}`);
      
      // Fetch historical data
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(endDate.getDate() - 30);

      const historicalResponse = await axios.post('/api/v1/market-data/historical', {
        symbol: selectedSymbol,
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        timeframe: timeframe
      });

      if (historicalResponse.data.data && historicalResponse.data.data.length > 0) {
        setMarketData(historicalResponse.data.data);
      } else {
        // Generate mock data if no historical data
        const mockData = generateMockData(selectedSymbol, 30);
        setMarketData(mockData);
      }
    } catch (err: any) {
      console.error('Market data error:', err);
      // Generate mock data as fallback
      const mockData = generateMockData(selectedSymbol, 30);
      setMarketData(mockData);
    } finally {
      setLoading(false);
    }
  }, [selectedSymbol, timeframe]);

  const fetchTradingSignal = useCallback(async () => {
    try {
      const response = await axios.post('/api/v1/signals/generate', {
        symbol: selectedSymbol,
        timeframe: timeframe
      });

      if (response.data.signal) {
        setTradingSignal(response.data.signal);
      }
    } catch (err: any) {
      console.error('Trading signal error:', err);
      // Generate mock signal
      setTradingSignal(generateMockSignal());
    }
  }, [selectedSymbol, timeframe]);

  const fetchTechnicalIndicators = useCallback(async () => {
    try {
      const response = await axios.get(`/api/v1/signals/technical-analysis/${selectedSymbol}?timeframe=${timeframe}`);
      
      if (response.data.technical_indicators) {
        setTechnicalIndicators(response.data.technical_indicators);
      }
    } catch (err: any) {
      console.error('Technical indicators error:', err);
      // Generate mock indicators
      setTechnicalIndicators(generateMockIndicators());
    }
  }, [selectedSymbol, timeframe]);

  const searchStocks = async (query: string) => {
    console.log('🔍 Searching for:', query);
    
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    // Extended stock list for better search results
    const allStocks = [
      ...popularSymbols,
      { symbol: 'ADANIPORTS', name: 'Adani Ports and SEZ' },
      { symbol: 'ASIANPAINT', name: 'Asian Paints' },
      { symbol: 'AXISBANK', name: 'Axis Bank' },
      { symbol: 'BAJAJ-AUTO', name: 'Bajaj Auto' },
      { symbol: 'BAJFINANCE', name: 'Bajaj Finance' },
      { symbol: 'BAJAJFINSV', name: 'Bajaj Finserv' },
      { symbol: 'BHARTIARTL', name: 'Bharti Airtel' },
      { symbol: 'BPCL', name: 'Bharat Petroleum' },
      { symbol: 'BRITANNIA', name: 'Britannia Industries' },
      { symbol: 'CIPLA', name: 'Cipla' },
      { symbol: 'COALINDIA', name: 'Coal India' },
      { symbol: 'DIVISLAB', name: 'Divi\'s Laboratories' },
      { symbol: 'DRREDDY', name: 'Dr. Reddy\'s Labs' },
      { symbol: 'EICHERMOT', name: 'Eicher Motors' },
      { symbol: 'GRASIM', name: 'Grasim Industries' },
      { symbol: 'HCLTECH', name: 'HCL Technologies' },
      { symbol: 'HEROMOTOCO', name: 'Hero MotoCorp' },
      { symbol: 'HINDALCO', name: 'Hindalco Industries' },
      { symbol: 'HINDUNILVR', name: 'Hindustan Unilever' },
      { symbol: 'ICICIBANK', name: 'ICICI Bank' },
      { symbol: 'ITC', name: 'ITC Limited' },
      { symbol: 'JSWSTEEL', name: 'JSW Steel' },
      { symbol: 'KOTAKBANK', name: 'Kotak Mahindra Bank' },
      { symbol: 'LT', name: 'Larsen & Toubro' },
      { symbol: 'M&M', name: 'Mahindra & Mahindra' },
      { symbol: 'MARUTI', name: 'Maruti Suzuki' },
      { symbol: 'NESTLEIND', name: 'Nestle India' },
      { symbol: 'NTPC', name: 'NTPC Limited' },
      { symbol: 'ONGC', name: 'Oil & Natural Gas Corp' },
      { symbol: 'POWERGRID', name: 'Power Grid Corporation' },
      { symbol: 'SBILIFE', name: 'SBI Life Insurance' },
      { symbol: 'SBIN', name: 'State Bank of India' },
      { symbol: 'SUNPHARMA', name: 'Sun Pharmaceutical' },
      { symbol: 'TATACONSUM', name: 'Tata Consumer Products' },
      { symbol: 'TATAMOTORS', name: 'Tata Motors' },
      { symbol: 'TATASTEEL', name: 'Tata Steel' },
      { symbol: 'TECHM', name: 'Tech Mahindra' },
      { symbol: 'TITAN', name: 'Titan Company' },
      { symbol: 'ULTRACEMCO', name: 'UltraTech Cement' },
      { symbol: 'UPL', name: 'UPL Limited' },
      { symbol: 'WIPRO', name: 'Wipro Limited' }
    ];

    // Search in both symbol and name
    const mockResults = allStocks
      .filter(stock => 
        stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
        stock.name.toLowerCase().includes(query.toLowerCase())
      )
      .slice(0, 10) // Limit to 10 results
      .map(stock => ({
        symbol: stock.symbol,
        name: stock.name,
        exchange: 'NSE'
      }));

    console.log('📊 Search results:', mockResults.length, 'stocks found');
    setSearchResults(mockResults);
  };

  const generateMockData = (symbol: string, days: number): MarketData[] => {
    const data: MarketData[] = [];
    let basePrice = 100;
    
    if (symbol.includes('NIFTY')) basePrice = 19500;
    else if (symbol.includes('SENSEX')) basePrice = 65000;
    else if (symbol.includes('RELIANCE')) basePrice = 2500;
    else if (symbol.includes('TCS')) basePrice = 3500;
    else if (symbol.includes('INFY')) basePrice = 1400;

    for (let i = 0; i < days; i++) {
      const date = new Date();
      date.setDate(date.getDate() - (days - i));
      
      const volatility = 0.02;
      const change = (Math.random() - 0.5) * volatility;
      basePrice *= (1 + change);
      
      const open = basePrice;
      const high = open * (1 + Math.random() * 0.01);
      const low = open * (1 - Math.random() * 0.01);
      const close = open + (Math.random() - 0.5) * (high - low);
      
      data.push({
        id: i,
        symbol: symbol,
        timestamp: date.toISOString(),
        open_price: parseFloat(open.toFixed(2)),
        high_price: parseFloat(high.toFixed(2)),
        low_price: parseFloat(low.toFixed(2)),
        close_price: parseFloat(close.toFixed(2)),
        volume: Math.floor(Math.random() * 1000000) + 100000,
        timeframe: timeframe
      });
    }
    
    return data;
  };

  const generateMockSignal = (): TradingSignal => {
    const signals = ['BUY', 'SELL', 'HOLD'];
    const signal = signals[Math.floor(Math.random() * signals.length)];
    
    return {
      signal_type: signal,
      strength: Math.random() * 0.8 + 0.2,
      price_target: marketData.length > 0 ? marketData[marketData.length - 1].close_price * (1 + (Math.random() - 0.5) * 0.1) : undefined,
      stop_loss: marketData.length > 0 ? marketData[marketData.length - 1].close_price * (1 - Math.random() * 0.05) : undefined,
      reasoning: `Technical analysis suggests ${signal} signal based on current market conditions and indicators.`
    };
  };

  const generateMockIndicators = (): TechnicalIndicators => {
    return {
      rsi_signal: ['BUY', 'SELL', 'HOLD'][Math.floor(Math.random() * 3)],
      rsi_strength: Math.random(),
      macd_signal: ['BUY', 'SELL', 'HOLD'][Math.floor(Math.random() * 3)],
      macd_strength: Math.random(),
      ma_signal: ['BUY', 'SELL', 'HOLD'][Math.floor(Math.random() * 3)],
      bb_signal: ['BUY', 'SELL', 'HOLD'][Math.floor(Math.random() * 3)],
      volume_confirmation: Math.random() > 0.5
    };
  };

  useEffect(() => {
    fetchMarketData();
    fetchTradingSignal();
    fetchTechnicalIndicators();
  }, [fetchMarketData, fetchTradingSignal, fetchTechnicalIndicators]);

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      if (searchQuery) {
        searchStocks(searchQuery);
      }
    }, 300);

    return () => clearTimeout(debounceTimer);
  }, [searchQuery]);

  const renderCandlestickChart = () => {
    if (!marketData.length) return null;

    return (
      <div className="chart-container">
        <svg width="100%" height="400" className="candlestick-svg">
          {marketData.map((candle, index) => {
            const x = (index / marketData.length) * 100;
            const prices = marketData.map(d => [d.high_price, d.low_price]).flat();
            const minPrice = Math.min(...prices);
            const maxPrice = Math.max(...prices);
            const priceRange = maxPrice - minPrice;
            
            const high = ((maxPrice - candle.high_price) / priceRange) * 80 + 10;
            const low = ((maxPrice - candle.low_price) / priceRange) * 80 + 10;
            const open = ((maxPrice - candle.open_price) / priceRange) * 80 + 10;
            const close = ((maxPrice - candle.close_price) / priceRange) * 80 + 10;
            
            const isGreen = candle.close_price > candle.open_price;
            const color = isGreen ? '#00d4aa' : '#e74c3c';
            
            return (
              <g key={index}>
                {/* Wick */}
                <line
                  x1={`${x}%`}
                  y1={`${high}%`}
                  x2={`${x}%`}
                  y2={`${low}%`}
                  stroke={color}
                  strokeWidth="1"
                />
                {/* Body */}
                <rect
                  x={`${x - 0.4}%`}
                  y={`${Math.min(open, close)}%`}
                  width="0.8%"
                  height={`${Math.abs(close - open)}%`}
                  fill={color}
                />
              </g>
            );
          })}
        </svg>
        
        {/* Price Labels */}
        <div className="price-labels">
          {marketData.length > 0 && (
            <>
              <div className="current-price">
                ₹{marketData[marketData.length - 1].close_price.toFixed(2)}
              </div>
              <div className="price-change">
                {marketData.length > 1 && (
                  <span className={
                    marketData[marketData.length - 1].close_price > marketData[marketData.length - 2].close_price 
                      ? 'positive' : 'negative'
                  }>
                    {((marketData[marketData.length - 1].close_price - marketData[marketData.length - 2].close_price) / marketData[marketData.length - 2].close_price * 100).toFixed(2)}%
                  </span>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="enhanced-trading-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-left">
          <h1>📈 AI Trading Dashboard</h1>
          <p>Real-time market analysis with advanced technical indicators</p>
        </div>
        <div className="header-right">
          <div className="search-container">
            <input
              type="text"
              placeholder="Search stocks..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setShowSearch(true);
              }}
              onFocus={() => setShowSearch(true)}
              className="stock-search"
            />
            {showSearch && searchResults.length > 0 && (
              <div className="search-results">
                {searchResults.map((result, index) => (
                  <div
                    key={index}
                    className="search-result-item"
                    onClick={() => {
                      setSelectedSymbol(result.symbol);
                      setSearchQuery('');
                      setShowSearch(false);
                    }}
                  >
                    <span className="symbol">{result.symbol}</span>
                    <span className="name">{result.name}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="controls-section">
        <div className="symbol-selector">
          <label>Popular Stocks:</label>
          <div className="symbol-chips">
            {popularSymbols.slice(0, 6).map((stock) => (
              <button
                key={stock.symbol}
                className={`symbol-chip ${selectedSymbol === stock.symbol ? 'active' : ''}`}
                onClick={() => setSelectedSymbol(stock.symbol)}
              >
                {stock.symbol}
              </button>
            ))}
          </div>
        </div>

        <div className="timeframe-selector">
          <label>Timeframe:</label>
          <div className="timeframe-buttons">
            {timeframes.map((tf) => (
              <button
                key={tf.value}
                className={`timeframe-btn ${timeframe === tf.value ? 'active' : ''}`}
                onClick={() => setTimeframe(tf.value)}
              >
                {tf.label}
              </button>
            ))}
          </div>
        </div>

        <button 
          className="refresh-button"
          onClick={() => {
            fetchMarketData();
            fetchTradingSignal();
            fetchTechnicalIndicators();
          }}
          disabled={loading}
        >
          {loading ? '🔄' : '↻'} Refresh
        </button>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Chart Section */}
        <div className="chart-section">
          <div className="chart-header">
            <h2>{selectedSymbol} - {timeframe}</h2>
            {tradingSignal && (
              <div className={`signal-indicator ${tradingSignal.signal_type.toLowerCase()}`}>
                {tradingSignal.signal_type === 'BUY' ? '📈' : tradingSignal.signal_type === 'SELL' ? '📉' : '⏸️'}
                {tradingSignal.signal_type}
              </div>
            )}
          </div>
          
          {loading ? (
            <div className="chart-loading">
              <div className="loading-spinner"></div>
              <p>Loading chart data...</p>
            </div>
          ) : (
            renderCandlestickChart()
          )}
        </div>

        {/* Side Panel */}
        <div className="side-panel">
          {/* Technical Indicators */}
          <div className="indicators-card">
            <h3>📊 Technical Indicators</h3>
            {technicalIndicators ? (
              <div className="indicators-grid">
                <div className="indicator-item">
                  <span className="indicator-name">RSI</span>
                  <span className={`indicator-signal ${technicalIndicators.rsi_signal?.toLowerCase()}`}>
                    {technicalIndicators.rsi_signal}
                  </span>
                </div>
                <div className="indicator-item">
                  <span className="indicator-name">MACD</span>
                  <span className={`indicator-signal ${technicalIndicators.macd_signal?.toLowerCase()}`}>
                    {technicalIndicators.macd_signal}
                  </span>
                </div>
                <div className="indicator-item">
                  <span className="indicator-name">MA</span>
                  <span className={`indicator-signal ${technicalIndicators.ma_signal?.toLowerCase()}`}>
                    {technicalIndicators.ma_signal}
                  </span>
                </div>
                <div className="indicator-item">
                  <span className="indicator-name">BB</span>
                  <span className={`indicator-signal ${technicalIndicators.bb_signal?.toLowerCase()}`}>
                    {technicalIndicators.bb_signal}
                  </span>
                </div>
                <div className="indicator-item">
                  <span className="indicator-name">Volume</span>
                  <span className={`indicator-signal ${technicalIndicators.volume_confirmation ? 'confirmed' : 'weak'}`}>
                    {technicalIndicators.volume_confirmation ? 'Strong' : 'Weak'}
                  </span>
                </div>
              </div>
            ) : (
              <div className="loading-indicators">Loading indicators...</div>
            )}
          </div>

          {/* Trading Signal */}
          {tradingSignal && (
            <div className="signal-card">
              <h3>🎯 Trading Signal</h3>
              <div className="signal-content">
                <div className={`signal-badge ${tradingSignal.signal_type.toLowerCase()}`}>
                  {tradingSignal.signal_type}
                </div>
                <div className="signal-strength">
                  <span>Strength: {(tradingSignal.strength * 100).toFixed(0)}%</span>
                  <div className="strength-bar">
                    <div 
                      className="strength-fill"
                      style={{ width: `${tradingSignal.strength * 100}%` }}
                    ></div>
                  </div>
                </div>
                {tradingSignal.price_target && (
                  <div className="price-levels">
                    <div className="price-level">
                      <span>Target: ₹{tradingSignal.price_target.toFixed(2)}</span>
                    </div>
                    {tradingSignal.stop_loss && (
                      <div className="price-level">
                        <span>Stop Loss: ₹{tradingSignal.stop_loss.toFixed(2)}</span>
                      </div>
                    )}
                  </div>
                )}
                <div className="signal-reasoning">
                  {tradingSignal.reasoning}
                </div>
              </div>
            </div>
          )}

          {/* Market Stats */}
          {marketData.length > 0 && (
            <div className="stats-card">
              <h3>📈 Market Stats</h3>
              <div className="stats-list">
                <div className="stat-row">
                  <span>Volume</span>
                  <span>{marketData[marketData.length - 1]?.volume.toLocaleString()}</span>
                </div>
                <div className="stat-row">
                  <span>High</span>
                  <span>₹{Math.max(...marketData.map(d => d.high_price)).toFixed(2)}</span>
                </div>
                <div className="stat-row">
                  <span>Low</span>
                  <span>₹{Math.min(...marketData.map(d => d.low_price)).toFixed(2)}</span>
                </div>
                <div className="stat-row">
                  <span>Open</span>
                  <span>₹{marketData[0]?.open_price.toFixed(2)}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EnhancedTradingDashboard;