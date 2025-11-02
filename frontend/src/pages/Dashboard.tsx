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
      // Mock data for market overview
      const mockData: MarketOverview[] = [
        { symbol: 'NIFTY50', price: 19547.30, change: 125.40, changePercent: 0.65 },
        { symbol: 'SENSEX', price: 65953.48, change: -89.83, changePercent: -0.14 },
        { symbol: 'RELIANCE', price: 2456.75, change: 23.50, changePercent: 0.97 },
        { symbol: 'TCS', price: 3542.20, change: -15.30, changePercent: -0.43 },
        { symbol: 'INFY', price: 1398.65, change: 8.90, changePercent: 0.64 },
        { symbol: 'HDFC', price: 1654.80, change: -12.45, changePercent: -0.75 }
      ];
      setMarketOverview(mockData);
    } catch (error) {
      console.error('Failed to fetch market overview:', error);
    }
  };

  const fetchRecentSignals = async () => {
    try {
      // Mock data for recent signals
      const mockSignals: RecentSignal[] = [
        { symbol: 'RELIANCE', signal_type: 'BUY', strength: 0.85, timestamp: new Date().toISOString() },
        { symbol: 'TCS', signal_type: 'HOLD', strength: 0.65, timestamp: new Date(Date.now() - 3600000).toISOString() },
        { symbol: 'INFY', signal_type: 'BUY', strength: 0.78, timestamp: new Date(Date.now() - 7200000).toISOString() },
        { symbol: 'HDFC', signal_type: 'SELL', strength: 0.72, timestamp: new Date(Date.now() - 10800000).toISOString() }
      ];
      setRecentSignals(mockSignals);
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
          
          <div className="action-card" onClick={() => window.location.reload()}>
            <div className="action-icon">🔄</div>
            <div className="action-title">Refresh Data</div>
            <div className="action-description">Update market data and signals</div>
          </div>
          
          <Link to="/dashboard" className="action-card">
            <div className="action-icon">📊</div>
            <div className="action-title">Analytics</div>
            <div className="action-description">View detailed market analysis</div>
          </Link>
          
          <div className="action-card">
            <div className="action-icon">⚙️</div>
            <div className="action-title">Settings</div>
            <div className="action-description">Configure preferences</div>
          </div>
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