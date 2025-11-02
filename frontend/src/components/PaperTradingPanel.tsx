import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface Position {
  id: string;
  symbol: string;
  type: 'BUY' | 'SELL';
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
  timestamp: string;
}

interface Order {
  id: string;
  symbol: string;
  type: 'BUY' | 'SELL';
  orderType: 'MARKET' | 'LIMIT' | 'STOP';
  quantity: number;
  price?: number;
  status: 'PENDING' | 'EXECUTED' | 'CANCELLED';
  timestamp: string;
}

interface PaperTradingPanelProps {
  selectedSymbol: string;
  currentPrice: number;
}

const PaperTradingPanel: React.FC<PaperTradingPanelProps> = ({ 
  selectedSymbol, 
  currentPrice 
}) => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'trade' | 'positions' | 'orders' | 'portfolio'>('trade');
  const [positions, setPositions] = useState<Position[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [portfolioValue, setPortfolioValue] = useState(100000); // Starting with 1 Lakh
  const [availableCash, setAvailableCash] = useState(100000);
  
  // Trade form state
  const [tradeType, setTradeType] = useState<'BUY' | 'SELL'>('BUY');
  const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT' | 'STOP'>('MARKET');
  const [quantity, setQuantity] = useState<number>(1);
  const [limitPrice, setLimitPrice] = useState<number>(currentPrice);
  const [stopPrice, setStopPrice] = useState<number>(currentPrice * 0.95);

  useEffect(() => {
    // Load saved data from localStorage
    const savedPositions = localStorage.getItem(`paperTrading_positions_${user?.id}`);
    const savedOrders = localStorage.getItem(`paperTrading_orders_${user?.id}`);
    const savedCash = localStorage.getItem(`paperTrading_cash_${user?.id}`);
    
    if (savedPositions) setPositions(JSON.parse(savedPositions));
    if (savedOrders) setOrders(JSON.parse(savedOrders));
    if (savedCash) setAvailableCash(parseFloat(savedCash));
  }, [user?.id]);

  useEffect(() => {
    // Update current prices and P&L for positions
    const updatedPositions = positions.map(position => {
      const pnl = (currentPrice - position.entryPrice) * position.quantity * (position.type === 'BUY' ? 1 : -1);
      const pnlPercent = (pnl / (position.entryPrice * position.quantity)) * 100;
      
      return {
        ...position,
        currentPrice,
        pnl,
        pnlPercent
      };
    });
    
    if (JSON.stringify(updatedPositions) !== JSON.stringify(positions)) {
      setPositions(updatedPositions);
    }
    
    // Calculate portfolio value
    const totalPnL = updatedPositions.reduce((sum, pos) => sum + pos.pnl, 0);
    setPortfolioValue(availableCash + totalPnL);
  }, [currentPrice, positions, availableCash]);

  const saveData = () => {
    localStorage.setItem(`paperTrading_positions_${user?.id}`, JSON.stringify(positions));
    localStorage.setItem(`paperTrading_orders_${user?.id}`, JSON.stringify(orders));
    localStorage.setItem(`paperTrading_cash_${user?.id}`, availableCash.toString());
  };

  const executeTrade = () => {
    const tradeValue = quantity * (orderType === 'MARKET' ? currentPrice : limitPrice);
    
    if (tradeType === 'BUY' && tradeValue > availableCash) {
      alert('Insufficient funds for this trade!');
      return;
    }

    const newPosition: Position = {
      id: Date.now().toString(),
      symbol: selectedSymbol,
      type: tradeType,
      quantity,
      entryPrice: orderType === 'MARKET' ? currentPrice : limitPrice,
      currentPrice,
      pnl: 0,
      pnlPercent: 0,
      timestamp: new Date().toISOString()
    };

    const newOrder: Order = {
      id: Date.now().toString(),
      symbol: selectedSymbol,
      type: tradeType,
      orderType,
      quantity,
      price: orderType === 'MARKET' ? currentPrice : limitPrice,
      status: 'EXECUTED',
      timestamp: new Date().toISOString()
    };

    setPositions(prev => [...prev, newPosition]);
    setOrders(prev => [...prev, newOrder]);
    
    if (tradeType === 'BUY') {
      setAvailableCash(prev => prev - tradeValue);
    } else {
      setAvailableCash(prev => prev + tradeValue);
    }

    // Reset form
    setQuantity(1);
    setLimitPrice(currentPrice);
    
    saveData();
    alert(`${tradeType} order executed successfully!`);
  };

  const closePosition = (positionId: string) => {
    const position = positions.find(p => p.id === positionId);
    if (!position) return;

    const closeValue = position.quantity * currentPrice;
    setAvailableCash(prev => prev + closeValue);
    setPositions(prev => prev.filter(p => p.id !== positionId));
    
    saveData();
    alert('Position closed successfully!');
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(amount);
  };

  return (
    <div className="paper-trading-panel">
      <div className="trading-header">
        <h3>📝 Paper Trading</h3>
        <div className="portfolio-summary">
          <div className="summary-item">
            <span>Portfolio Value</span>
            <span className="value">{formatCurrency(portfolioValue)}</span>
          </div>
          <div className="summary-item">
            <span>Available Cash</span>
            <span className="value">{formatCurrency(availableCash)}</span>
          </div>
        </div>
      </div>

      <div className="trading-tabs">
        {['trade', 'positions', 'orders', 'portfolio'].map(tab => (
          <button
            key={tab}
            className={`tab-button ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab as any)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <div className="tab-content">
        {activeTab === 'trade' && (
          <div className="trade-form">
            <div className="symbol-info">
              <h4>{selectedSymbol}</h4>
              <span className="current-price">{formatCurrency(currentPrice)}</span>
            </div>

            <div className="trade-controls">
              <div className="trade-type-selector">
                <button
                  className={`trade-btn ${tradeType === 'BUY' ? 'buy active' : 'buy'}`}
                  onClick={() => setTradeType('BUY')}
                >
                  BUY
                </button>
                <button
                  className={`trade-btn ${tradeType === 'SELL' ? 'sell active' : 'sell'}`}
                  onClick={() => setTradeType('SELL')}
                >
                  SELL
                </button>
              </div>

              <div className="order-type-selector">
                <select 
                  value={orderType} 
                  onChange={(e) => setOrderType(e.target.value as any)}
                >
                  <option value="MARKET">Market Order</option>
                  <option value="LIMIT">Limit Order</option>
                  <option value="STOP">Stop Order</option>
                </select>
              </div>

              <div className="quantity-input">
                <label>Quantity</label>
                <input
                  type="number"
                  min="1"
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                />
              </div>

              {orderType === 'LIMIT' && (
                <div className="price-input">
                  <label>Limit Price</label>
                  <input
                    type="number"
                    step="0.01"
                    value={limitPrice}
                    onChange={(e) => setLimitPrice(parseFloat(e.target.value) || currentPrice)}
                  />
                </div>
              )}

              {orderType === 'STOP' && (
                <div className="price-input">
                  <label>Stop Price</label>
                  <input
                    type="number"
                    step="0.01"
                    value={stopPrice}
                    onChange={(e) => setStopPrice(parseFloat(e.target.value) || currentPrice)}
                  />
                </div>
              )}

              <div className="trade-summary">
                <div className="summary-row">
                  <span>Total Value:</span>
                  <span>{formatCurrency(quantity * (orderType === 'MARKET' ? currentPrice : limitPrice))}</span>
                </div>
              </div>

              <button 
                className={`execute-btn ${tradeType.toLowerCase()}`}
                onClick={executeTrade}
              >
                {tradeType} {quantity} shares
              </button>
            </div>
          </div>
        )}

        {activeTab === 'positions' && (
          <div className="positions-list">
            {positions.length === 0 ? (
              <div className="empty-state">
                <p>No open positions</p>
              </div>
            ) : (
              positions.map(position => (
                <div key={position.id} className="position-item">
                  <div className="position-header">
                    <span className="symbol">{position.symbol}</span>
                    <span className={`type ${position.type.toLowerCase()}`}>
                      {position.type}
                    </span>
                  </div>
                  <div className="position-details">
                    <div className="detail-row">
                      <span>Quantity: {position.quantity}</span>
                      <span>Entry: {formatCurrency(position.entryPrice)}</span>
                    </div>
                    <div className="detail-row">
                      <span>Current: {formatCurrency(position.currentPrice)}</span>
                      <span className={position.pnl >= 0 ? 'profit' : 'loss'}>
                        P&L: {formatCurrency(position.pnl)} ({position.pnlPercent.toFixed(2)}%)
                      </span>
                    </div>
                  </div>
                  <button 
                    className="close-btn"
                    onClick={() => closePosition(position.id)}
                  >
                    Close Position
                  </button>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'orders' && (
          <div className="orders-list">
            {orders.length === 0 ? (
              <div className="empty-state">
                <p>No orders placed</p>
              </div>
            ) : (
              orders.slice(-10).reverse().map(order => (
                <div key={order.id} className="order-item">
                  <div className="order-header">
                    <span className="symbol">{order.symbol}</span>
                    <span className={`status ${order.status.toLowerCase()}`}>
                      {order.status}
                    </span>
                  </div>
                  <div className="order-details">
                    <span>{order.type} {order.quantity} @ {formatCurrency(order.price || 0)}</span>
                    <span className="timestamp">
                      {new Date(order.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'portfolio' && (
          <div className="portfolio-overview">
            <div className="portfolio-stats">
              <div className="stat-card">
                <h4>Total Portfolio Value</h4>
                <span className="value">{formatCurrency(portfolioValue)}</span>
              </div>
              <div className="stat-card">
                <h4>Available Cash</h4>
                <span className="value">{formatCurrency(availableCash)}</span>
              </div>
              <div className="stat-card">
                <h4>Total P&L</h4>
                <span className={`value ${portfolioValue - 100000 >= 0 ? 'profit' : 'loss'}`}>
                  {formatCurrency(portfolioValue - 100000)}
                </span>
              </div>
              <div className="stat-card">
                <h4>Active Positions</h4>
                <span className="value">{positions.length}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PaperTradingPanel;