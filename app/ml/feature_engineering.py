"""
Feature engineering and technical indicators for ML models
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import structlog

logger = structlog.get_logger()


class TechnicalIndicators:
    """Technical indicators calculation for market data"""
    
    @staticmethod
    def sma(data: pd.Series, window: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(window=window).mean()
    
    @staticmethod
    def ema(data: pd.Series, window: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=window).mean()
    
    @staticmethod
    def rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD (Moving Average Convergence Divergence)"""
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def bollinger_bands(data: pd.Series, window: int = 20, num_std: float = 2) -> Dict[str, pd.Series]:
        """Bollinger Bands"""
        sma = TechnicalIndicators.sma(data, window)
        std = data.rolling(window=window).std()
        
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    
    @staticmethod
    def stochastic_oscillator(high: pd.Series, low: pd.Series, close: pd.Series, k_window: int = 14, d_window: int = 3) -> Dict[str, pd.Series]:
        """Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_window).mean()
        
        return {
            'k_percent': k_percent,
            'd_percent': d_percent
        }
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """Average True Range"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=window).mean()
        
        return atr
    
    @staticmethod
    def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """Williams %R"""
        highest_high = high.rolling(window=window).max()
        lowest_low = low.rolling(window=window).min()
        
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        return williams_r


class FeatureExtractor:
    """Feature extraction for ML models"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
    
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract comprehensive features from OHLCV data"""
        try:
            logger.info("Starting feature extraction", records=len(df))
            
            # Ensure required columns exist
            required_cols = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Missing required column: {col}")
            
            # Create feature dataframe
            features_df = df.copy()
            
            # Price-based features
            features_df['price_change'] = df['close_price'].pct_change()
            features_df['price_range'] = (df['high_price'] - df['low_price']) / df['close_price']
            features_df['body_size'] = np.abs(df['close_price'] - df['open_price']) / df['close_price']
            features_df['upper_shadow'] = (df['high_price'] - np.maximum(df['open_price'], df['close_price'])) / df['close_price']
            features_df['lower_shadow'] = (np.minimum(df['open_price'], df['close_price']) - df['low_price']) / df['close_price']
            
            # Volume features
            features_df['volume_change'] = df['volume'].pct_change()
            features_df['volume_price_trend'] = df['volume'] * features_df['price_change']
            
            # Moving averages
            for window in [5, 10, 20, 50]:
                features_df[f'sma_{window}'] = self.indicators.sma(df['close_price'], window)
                features_df[f'ema_{window}'] = self.indicators.ema(df['close_price'], window)
                features_df[f'price_to_sma_{window}'] = df['close_price'] / features_df[f'sma_{window}']
                features_df[f'volume_sma_{window}'] = self.indicators.sma(df['volume'], window)
            
            # Technical indicators
            features_df['rsi'] = self.indicators.rsi(df['close_price'])
            
            # MACD
            macd_data = self.indicators.macd(df['close_price'])
            features_df['macd'] = macd_data['macd']
            features_df['macd_signal'] = macd_data['signal']
            features_df['macd_histogram'] = macd_data['histogram']
            
            # Bollinger Bands
            bb_data = self.indicators.bollinger_bands(df['close_price'])
            features_df['bb_upper'] = bb_data['upper']
            features_df['bb_middle'] = bb_data['middle']
            features_df['bb_lower'] = bb_data['lower']
            features_df['bb_width'] = (bb_data['upper'] - bb_data['lower']) / bb_data['middle']
            features_df['bb_position'] = (df['close_price'] - bb_data['lower']) / (bb_data['upper'] - bb_data['lower'])
            
            # Stochastic Oscillator
            stoch_data = self.indicators.stochastic_oscillator(
                df['high_price'], df['low_price'], df['close_price']
            )
            features_df['stoch_k'] = stoch_data['k_percent']
            features_df['stoch_d'] = stoch_data['d_percent']
            
            # ATR
            features_df['atr'] = self.indicators.atr(
                df['high_price'], df['low_price'], df['close_price']
            )
            features_df['atr_ratio'] = features_df['atr'] / df['close_price']
            
            # Williams %R
            features_df['williams_r'] = self.indicators.williams_r(
                df['high_price'], df['low_price'], df['close_price']
            )
            
            # Lag features
            for lag in [1, 2, 3, 5]:
                features_df[f'close_lag_{lag}'] = df['close_price'].shift(lag)
                features_df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
                features_df[f'price_change_lag_{lag}'] = features_df['price_change'].shift(lag)
            
            # Rolling statistics
            for window in [5, 10, 20]:
                features_df[f'price_std_{window}'] = df['close_price'].rolling(window).std()
                features_df[f'price_min_{window}'] = df['close_price'].rolling(window).min()
                features_df[f'price_max_{window}'] = df['close_price'].rolling(window).max()
                features_df[f'volume_std_{window}'] = df['volume'].rolling(window).std()
            
            # Time-based features
            if 'timestamp' in df.columns:
                features_df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
                features_df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
                features_df['month'] = pd.to_datetime(df['timestamp']).dt.month
            
            logger.info("Feature extraction completed", features=len(features_df.columns))
            return features_df
            
        except Exception as e:
            logger.error("Feature extraction failed", error=str(e))
            raise
    
    def create_target_variables(self, df: pd.DataFrame, horizons: List[int] = [1, 5, 10]) -> pd.DataFrame:
        """Create target variables for different prediction horizons"""
        try:
            targets_df = df.copy()
            
            for horizon in horizons:
                # Price change targets
                targets_df[f'price_change_{horizon}'] = df['close_price'].shift(-horizon) / df['close_price'] - 1
                
                # Direction targets (binary classification)
                targets_df[f'direction_{horizon}'] = (targets_df[f'price_change_{horizon}'] > 0).astype(int)
                
                # Volatility targets
                future_prices = df['close_price'].rolling(window=horizon).apply(
                    lambda x: x.iloc[-1] if len(x) == horizon else np.nan
                ).shift(-horizon)
                targets_df[f'volatility_{horizon}'] = (
                    df['close_price'].rolling(window=horizon).std().shift(-horizon) / df['close_price']
                )
            
            return targets_df
            
        except Exception as e:
            logger.error("Target variable creation failed", error=str(e))
            raise
    
    def preprocess_features(self, df: pd.DataFrame, fit_scaler: bool = True) -> Tuple[pd.DataFrame, Dict]:
        """Preprocess features for ML models"""
        try:
            from sklearn.preprocessing import StandardScaler, RobustScaler
            from sklearn.impute import SimpleImputer
            
            # Remove non-numeric columns for scaling
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df_numeric = df[numeric_cols].copy()
            
            # Handle missing values
            imputer = SimpleImputer(strategy='median')
            df_imputed = pd.DataFrame(
                imputer.fit_transform(df_numeric),
                columns=df_numeric.columns,
                index=df_numeric.index
            )
            
            # Scale features
            scaler = RobustScaler()  # More robust to outliers than StandardScaler
            
            if fit_scaler:
                df_scaled = pd.DataFrame(
                    scaler.fit_transform(df_imputed),
                    columns=df_imputed.columns,
                    index=df_imputed.index
                )
            else:
                df_scaled = df_imputed
            
            # Store preprocessing objects
            preprocessing_objects = {
                'imputer': imputer,
                'scaler': scaler if fit_scaler else None,
                'feature_columns': list(df_scaled.columns)
            }
            
            logger.info("Feature preprocessing completed", features=len(df_scaled.columns))
            return df_scaled, preprocessing_objects
            
        except Exception as e:
            logger.error("Feature preprocessing failed", error=str(e))
            raise
    
    def get_feature_importance_names(self) -> List[str]:
        """Get list of feature names for importance analysis"""
        return [
            'price_change', 'price_range', 'body_size', 'upper_shadow', 'lower_shadow',
            'volume_change', 'volume_price_trend', 'rsi', 'macd', 'macd_signal', 'macd_histogram',
            'bb_width', 'bb_position', 'stoch_k', 'stoch_d', 'atr_ratio', 'williams_r'
        ]