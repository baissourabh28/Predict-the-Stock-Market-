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
    const totalPnL = updatedPositions.reduce((sum, pos) => sum +