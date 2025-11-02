import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';
import axios from 'axios';

interface MarketOverview {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
}

interface RecentSignal {
  symbol: string;
  signal_type: string;
  strength: number;
  timestamp: string;
}

interface PortfolioStats {
  totalValue: number;
  dayChange: number;
  dayChangePercent: number;
  totalGainLoss: number;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [apiStatus, setApiStatus] = useState<string>('checking...');
  const [marketOverview, setMarketOverview] = useState<MarketOverview[]>([]);
  const [recentSignals, setRecentSignals] = useState<RecentSignal[]>([]);
  const [portfolioStats, setPortfolioStats] = useState<PortfolioStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeDashboard = async () => {
      await checkApiHealth();
      await fetchMarketOverview();
      await fetchRecentSignals();
      await fetchPortfolioStats();
      setLoading(false);
    };

    initializeDashboard();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await axios.get('/api/v1/health');
      setApiStatus('connected');
    } catch (error) {
      setApiStatus('disconnected');
    }
  };

  const fetchMarketOverview = async () => {
    try {
      console.log('🔄 Refreshing market data...');
      const symbols = ['NIFTY50', 'SENSEX', 'RELIANCE', 'TCS', 'INFY', 'HDFC'];
      const marketData: MarketOverview[] = [];
      
      // Generate dynamic realistic data with variations
      const baseData = {
        'NIFTY50': 19547.30,
        'SENSEX': 65953.48,
        'RELIANCE': 2456.75,
        'TCS': 3542.20,
        'INFY': 1398.65,
        'HDFC': 1654.80
      };

      for (const symbol of symbols) {
        const basePrice = baseData[symbol as keyof typeof baseData];
        // Generate realistic price variations (-3% to +3%)
        const variation = (Math.random() - 0.5) * 0.06;
        const newPrice = basePrice * (1 + variation);
        const change = newPrice - basePrice;
        const changePercent = (change / basePrice) * 100;

        marketData.push({
          symbol: symbol,
          price: parseFloat(newPrice.toFixed(2)),
          change: parseFloat(change.toFixed(2)),
          changePercent: parseFloat(changePercent.toFixed(2))
        });
      }
      
      setMarketOverview(marketData);
      console.log('✅ Market data refreshed successfully');
    } catch (error) {
      console.error('Failed to fetch market overview:', error);
    }
  };

  const fetchRecentSignals = async () => {
    try {
      console.log('🎯 Refreshing trading signals...');
      const symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'NIFTY50', 'SENSEX'];
      const signalTypes = ['BUY', 'SELL', 'HOLD'];
      
      // Generate dynamic signals
      const mockSignals: RecentSignal[] = symbols.slice(0, 4).map((symbol, index) => ({
        symbol: symbol,
        signal_type: signalTypes[Math.floor(Math.random() * signalTypes.length)],
        strength: parseFloat((0.5 + Math.random() * 0.4).toFixed(2)), // 0.5 to 0.9
        timestamp: new Date(Date.now() - (index * 1800000)).toISOString() // 30 min intervals
      }));
      
      setRecentSignals(mockSignals);
      console.log('✅ Trading signals refreshed');
    } catch (error) {
      console.error('Failed to fetch recent signals:', error);
    }
  };

  const fetchPortfolioStats = async () => {
    try {
      // Mock portfolio data
      const mockStats: PortfolioStats = {
        totalValue: 125000,
        dayChange: 2340.50,
        dayChangePercent: 1.91,
        totalGainLoss: 15750.25
      };
      setPortfolioStats(mockStats);
    } catch (error) {
      console.error('Failed to fetch portfolio stats:', error);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading-dashboard">
          <div className="spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container dashboard-container">
      {/* Header Section */}
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1>📊 Trading Dashboard</h1>
          <p>Welcome back, <strong>{user?.username}</strong>! Here's your market overview.</p>
        </div>
        <div className="status-indicator">
          <div className={`status-dot ${apiStatus === 'connected' ? 'connected' : 'disconnected'}`}></div>
          <span>API {apiStatus}</span>
        </div>
      </div>

      {/* Portfolio Overview */}
      {portfolioStats && (
        <div className="portfolio-overview">
          <div className="portfolio-card">
            <h3>💼 Portfolio Value</h3>
            <div className="portfolio-value">
              {formatCurrency(portfolioStats.totalValue)}
            </div>
            <div className={`portfolio-change ${portfolioStats.dayChange >= 0 ? 'positive' : 'negative'}`}>
              {portfolioStats.dayChange >= 0 ? '↗' : '↘'} 
              {formatCurrency(Math.abs(portfolioStats.dayChange))} 
              ({portfolioStats.dayChangePercent.toFixed(2)}%)
            </div>
          </div>
          
          <div className="portfolio-card">
            <h3>📈 Total P&L</h3>
            <div className={`portfolio-value ${portfolioStats.totalGainLoss >= 0 ? 'positive' : 'negative'}`}>
              {formatCurrency(portfolioStats.totalGainLoss)}
            </div>
            <div className="portfolio-subtitle">
              Since inception
            </div>
          </div>

          <div className="portfolio-card">
            <h3>🎯 Active Positions</h3>
            <div className="portfolio-value">
              8
            </div>
            <div className="portfolio-subtitle">
              Stocks in portfolio
            </div>
          </div>
        </div>
      )}

      {/* Market Overview */}
      <div className="market-overview-section">
        <h2>🏪 Market Overview</h2>
        <div className="market-grid">
          {marketOverview.map((stock, index) => (
            <div key={index} className="market-card">
              <div className="stock-symbol">{stock.symbol}</div>
              <div className="stock-price">{formatCurrency(stock.price)}</div>
              <div className={`stock-change ${stock.change >= 0 ? 'positive' : 'negative'}`}>
                {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)} 
                ({stock.changePercent.toFixed(2)}%)
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Signals */}
      <div className="signals-section">
        <div className="section-header">
          <h2>🎯 Recent Trading Signals</h2>
          <Link to="/trading" className="view-all-link">View All →</Link>
        </div>
        <div className="signals-list">
          {recentSignals.map((signal, index) => (
            <div key={index} className="signal-item">
              <div className="signal-symbol">{signal.symbol}</div>
              <div className={`signal-type ${signal.signal_type.toLowerCase()}`}>
                {signal.signal_type === 'BUY' ? '📈' : signal.signal_type === 'SELL' ? '📉' : '⏸️'}
                {signal.signal_type}
              </div>
              <div className="signal-strength">
                <div className="strength-bar">
                  <div 
                    className="strength-fill"
                    style={{ width: `${signal.strength * 100}%` }}
                  ></div>
                </div>
                <span>{(signal.strength * 100).toFixed(0)}%</span>
              </div>
              <div className="signal-time">{formatTime(signal.timestamp)}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions-section">
        <h2>⚡ Quick Actions</h2>
        <div className="actions-grid">
          <Link to="/trading" className="action-card">
            <div className="action-icon">📈</div>
            <div className="action-title">Live Trading</div>
            <div className="action-description">View charts and generate signals</div>
          </Link>
          
          <div className="action-card" onClick={async () => {
            setLoading(true);
            await checkApiHealth();
            await fetchMarketOverview();
            await fetchRecentSignals();
            await fetchPortfolioStats();
            setLoading(false);
          }}>
            <div className="action-icon">🔄</div>
            <div className="action-title">Refresh Data</div>
            <div className="action-description">Update market data and signals</div>
          </div>
          
          <Link to="/dashboard" className="action-card">
            <div className="action-icon">📊</div>
            <div className="action-title">Analytics</div>
            <div className="action-description">View detailed market analysis</div>
          </Link>
          
          <Link to="/settings" className="action-card">
            <div className="action-icon">⚙️</div>
            <div className="action-title">Settings</div>
            <div className="action-description">Configure preferences</div>
          </Link>
        </div>
      </div>

      {/* System Information */}
      <div className="system-info-section">
        <h3>🔧 System Information</h3>
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">User ID:</span>
            <span className="info-value">{user?.id}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Email:</span>
            <span className="info-value">{user?.email}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Account Created:</span>
            <span className="info-value">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
            </span>
          </div>
          <div className="info-item">
            <span className="info-label">Last Login:</span>
            <span className="info-value">
              {new Date().toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;