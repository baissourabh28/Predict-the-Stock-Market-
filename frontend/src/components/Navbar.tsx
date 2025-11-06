import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
    setIsMenuOpen(false);
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <nav className="modern-navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">📈</span>
          <span className="logo-text">Stock Market Candlestick Prediction with AI/ML </span>
        </Link>
        
        <div className={`navbar-menu ${isMenuOpen ? 'active' : ''}`}>
          {user ? (
            <>
              <Link 
                to="/dashboard" 
                className={`nav-item ${isActive('/dashboard') ? 'active' : ''}`}
                onClick={() => setIsMenuOpen(false)}
              >
                <span className="nav-icon">📊</span>
                Dashboard
              </Link>
              <Link 
                to="/trading" 
                className={`nav-item ${isActive('/trading') || isActive('/') ? 'active' : ''}`}
                onClick={() => setIsMenuOpen(false)}
              >
                <span className="nav-icon">📈</span>
                Trading
              </Link>
              <Link 
                to="/settings" 
                className={`nav-item ${isActive('/settings') ? 'active' : ''}`}
                onClick={() => setIsMenuOpen(false)}
              >
                <span className="nav-icon">⚙️</span>
                Settings
              </Link>
              
              <div className="user-section">
                <div className="user-info">
                  <div className="user-avatar">
                    {user.username.charAt(0).toUpperCase()}
                  </div>
                  <span className="user-name">{user.username}</span>
                </div>
                <button onClick={handleLogout} className="logout-btn">
                  <span className="logout-icon">🚪</span>
                  Logout
                </button>
              </div>
            </>
          ) : (
            <div className="auth-links">
              <Link 
                to="/login" 
                className={`nav-item ${isActive('/login') ? 'active' : ''}`}
                onClick={() => setIsMenuOpen(false)}
              >
                Login
              </Link>
              <Link 
                to="/register" 
                className={`nav-item register-btn ${isActive('/register') ? 'active' : ''}`}
                onClick={() => setIsMenuOpen(false)}
              >
                Register
              </Link>
            </div>
          )}
        </div>

        <button 
          className="mobile-menu-btn"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
    </nav>
  );
};

export default Navbar;