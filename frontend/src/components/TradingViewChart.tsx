import React, { useEffect, useRef, useState } from 'react';
import { marketDataService, MarketTick, CandleData } from '../services/MarketDataService';

// CandleData interface is now imported from MarketDataService

interface TradingViewChartProps {
  symbol: string;
  timeframe: string;
  onPriceUpdate?: (price: number) => void;
}

const TradingViewChart: React.FC<TradingViewChartProps> = ({ 
  symbol, 
  timeframe, 
  onPriceUpdate 
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [candleData, setCandleData] = useState<CandleData[]>([]);
  const [currentPrice, setCurrentPrice] = useState<number>(0);
  const [priceChange, setPriceChange] = useState<number>(0);
  const [changePercent, setChangePercent] = useState<number>(0);
  const [volume, setVolume] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const [marketStatus, setMarketStatus] = useState<string>('');
  const [lastUpdate, setLastUpdate] = useState<string>('');

  // Load historical data and subscribe to real-time updates
  useEffect(() => {
    setIsLoading(true);
    
    // Load historical data
    const historicalData = marketDataService.generateHistoricalData(symbol, 100);
    setCandleData(historicalData);
    
    // Set initial market status
    setMarketStatus(marketDataService.getMarketStatus());
    
    // Subscribe to real-time price updates
    const unsubscribe = marketDataService.subscribe(symbol, (tick: MarketTick) => {
      setCurrentPrice(tick.price);
      setPriceChange(tick.change);
      setChangePercent(tick.changePercent);
      setVolume(tick.volume);
      setLastUpdate(new Date(tick.timestamp).toLocaleTimeString());
      
      // Update parent component
      onPriceUpdate?.(tick.price);
      
      // Update the last candle with real-time price
      setCandleData(prevData => {
        if (prevData.length === 0) return prevData;
        
        const updatedData = [...prevData];
        const lastCandle = updatedData[updatedData.length - 1];
        
        updatedData[updatedData.length - 1] = {
          ...lastCandle,
          close: tick.price,
          high: Math.max(lastCandle.high, tick.price),
          low: Math.min(lastCandle.low, tick.price),
          volume: tick.volume
        };
        
        return updatedData;
      });
    });
    
    setIsLoading(false);
    
    // Cleanup subscription on unmount or symbol change
    return () => {
      unsubscribe();
    };
  }, [symbol, onPriceUpdate]);

  // Update market status periodically
  useEffect(() => {
    const statusInterval = setInterval(() => {
      setMarketStatus(marketDataService.getMarketStatus());
    }, 60000); // Update every minute
    
    return () => clearInterval(statusInterval);
  }, []);

  // Draw the chart
  useEffect(() => {
    if (!canvasRef.current || candleData.length === 0) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Set canvas size
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    
    const width = rect.width;
    const height = rect.height;
    
    // Clear canvas
    ctx.fillStyle = '#1a1f2e';
    ctx.fillRect(0, 0, width, height);
    
    // Calculate price range
    const prices = candleData.flatMap(d => [d.high, d.low]);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice;
    const padding = priceRange * 0.1;
    
    const chartMinPrice = minPrice - padding;
    const chartMaxPrice = maxPrice + padding;
    const chartPriceRange = chartMaxPrice - chartMinPrice;
    
    // Draw grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    
    // Horizontal grid lines (price levels)
    for (let i = 0; i <= 10; i++) {
      const y = (height * i) / 10;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
      
      // Price labels
      const price = chartMaxPrice - (chartPriceRange * i) / 10;
      ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
      ctx.font = '12px Arial';
      ctx.fillText(price.toFixed(2), width - 60, y + 4);
    }
    
    // Vertical grid lines (time)
    const visibleCandles = Math.min(candleData.length, 50);
    const candleWidth = width / visibleCandles;
    
    for (let i = 0; i < visibleCandles; i += 5) {
      const x = i * candleWidth;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    
    // Draw candlesticks
    const startIndex = Math.max(0, candleData.length - visibleCandles);
    
    for (let i = startIndex; i < candleData.length; i++) {
      const candle = candleData[i];
      const x = (i - startIndex) * candleWidth;
      const centerX = x + candleWidth / 2;
      
      // Calculate Y positions
      const openY = height - ((candle.open - chartMinPrice) / chartPriceRange) * height;
      const closeY = height - ((candle.close - chartMinPrice) / chartPriceRange) * height;
      const highY = height - ((candle.high - chartMinPrice) / chartPriceRange) * height;
      const lowY = height - ((candle.low - chartMinPrice) / chartPriceRange) * height;
      
      const isGreen = candle.close > candle.open;
      const color = isGreen ? '#00d4aa' : '#e74c3c';
      
      // Draw wick
      ctx.strokeStyle = color;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(centerX, highY);
      ctx.lineTo(centerX, lowY);
      ctx.stroke();
      
      // Draw body
      ctx.fillStyle = color;
      const bodyTop = Math.min(openY, closeY);
      const bodyHeight = Math.abs(closeY - openY);
      const bodyWidth = candleWidth * 0.6;
      
      ctx.fillRect(
        centerX - bodyWidth / 2,
        bodyTop,
        bodyWidth,
        Math.max(bodyHeight, 1)
      );
    }
    
    // Draw current price line
    if (currentPrice > 0) {
      const priceY = height - ((currentPrice - chartMinPrice) / chartPriceRange) * height;
      
      ctx.strokeStyle = '#ffd700';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(0, priceY);
      ctx.lineTo(width, priceY);
      ctx.stroke();
      ctx.setLineDash([]);
      
      // Price label
      ctx.fillStyle = '#ffd700';
      ctx.fillRect(width - 80, priceY - 12, 75, 24);
      ctx.fillStyle = '#000';
      ctx.font = 'bold 12px Arial';
      ctx.fillText(currentPrice.toFixed(2), width - 75, priceY + 4);
    }
    
  }, [candleData, currentPrice]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(amount);
  };

  if (isLoading) {
    return (
      <div className="chart-loading">
        <div className="loading-spinner"></div>
        <p>Loading market data...</p>
      </div>
    );
  }

  return (
    <div className="tradingview-chart" ref={chartContainerRef}>
      <div className="chart-header">
        <div className="symbol-info">
          <h3>{symbol}</h3>
          <span className="timeframe">{timeframe}</span>
        </div>
        <div className="price-info">
          <span className="current-price">{formatCurrency(currentPrice)}</span>
          <span className={`price-change ${priceChange >= 0 ? 'positive' : 'negative'}`}>
            {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)} 
            ({((priceChange / currentPrice) * 100).toFixed(2)}%)
          </span>
        </div>
        <div className="volume-info">
          <span>Volume: {volume.toLocaleString()}</span>
        </div>
      </div>
      
      <div className="chart-container">
        <canvas 
          ref={canvasRef}
          className="price-chart"
        />
      </div>
      
      <div className="chart-controls">
        <div className="timeframe-buttons">
          {['1m', '5m', '15m', '1H', '1D', '1W'].map(tf => (
            <button 
              key={tf}
              className={`tf-btn ${timeframe === tf ? 'active' : ''}`}
            >
              {tf}
            </button>
          ))}
        </div>
        
        <div className="chart-tools">
          <button className="tool-btn">📏 Measure</button>
          <button className="tool-btn">📈 Trend Line</button>
          <button className="tool-btn">📊 Indicators</button>
        </div>
      </div>
    </div>
  );
};

export default TradingViewChart;