"""
Trading signal generation service with support and resistance levels
"""
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import structlog

from app.models.market_data import MarketData
from app.schemas.market_data import TradingSignalSchema, SignalTypeEnum
from app.ml.feature_engineering import TechnicalIndicators

logger = structlog.get_logger()


class SupportResistanceCalculator:
    """Calculate support and resistance levels from market data"""
    
    @staticmethod
    def find_pivot_points(highs: pd.Series, lows: pd.Series, window: int = 5) -> Tuple[List[float], List[float]]:
        """Find pivot highs and lows"""
        pivot_highs = []
        pivot_lows = []
        
        for i in range(window, len(highs) - window):
            # Check for pivot high
            if all(highs.iloc[i] >= highs.iloc[i-j] for j in range(1, window+1)) and \
               all(highs.iloc[i] >= highs.iloc[i+j] for j in range(1, window+1)):
                pivot_highs.append(highs.iloc[i])
            
            # Check for pivot low
            if all(lows.iloc[i] <= lows.iloc[i-j] for j in range(1, window+1)) and \
               all(lows.iloc[i] <= lows.iloc[i+j] for j in range(1, window+1)):
                pivot_lows.append(lows.iloc[i])
        
        return pivot_highs, pivot_lows
    
    @staticmethod
    def calculate_support_resistance(market_data: List[MarketData], lookback_periods: int = 50) -> Dict[str, List[float]]:
        """Calculate support and resistance levels"""
        try:
            if len(market_data) < lookback_periods:
                lookback_periods = len(market_data)
            
            # Get recent data
            recent_data = market_data[-lookback_periods:]
            
            highs = pd.Series([data.high_price for data in recent_data])
            lows = pd.Series([data.low_price for data in recent_data])
            closes = pd.Series([data.close_price for data in recent_data])
            
            # Find pivot points
            pivot_highs, pivot_lows = SupportResistanceCalculator.find_pivot_points(highs, lows)
            
            # Cluster similar levels
            resistance_levels = SupportResistanceCalculator._cluster_levels(pivot_highs, tolerance=0.02)
            support_levels = SupportResistanceCalculator._cluster_levels(pivot_lows, tolerance=0.02)
            
            # Add moving average levels
            current_price = closes.iloc[-1]
            
            # Add key moving averages as dynamic support/resistance
            ma_20 = closes.rolling(20).mean().iloc[-1] if len(closes) >= 20 else current_price
            ma_50 = closes.rolling(50).mean().iloc[-1] if len(closes) >= 50 else current_price
            
            if ma_20 > current_price:
                resistance_levels.append(ma_20)
            else:
                support_levels.append(ma_20)
            
            if ma_50 > current_price:
                resistance_levels.append(ma_50)
            else:
                support_levels.append(ma_50)
            
            # Sort and filter levels
            resistance_levels = sorted([level for level in resistance_levels if level > current_price])[:3]
            support_levels = sorted([level for level in support_levels if level < current_price], reverse=True)[:3]
            
            return {
                'support_levels': support_levels,
                'resistance_levels': resistance_levels,
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error("Failed to calculate support/resistance", error=str(e))
            return {'support_levels': [], 'resistance_levels': [], 'current_price': 0}
    
    @staticmethod
    def _cluster_levels(levels: List[float], tolerance: float = 0.02) -> List[float]:
        """Cluster similar price levels"""
        if not levels:
            return []
        
        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - current_cluster[-1]) / current_cluster[-1] <= tolerance:
                current_cluster.append(level)
            else:
                # Average the cluster
                clustered.append(sum(current_cluster) / len(current_cluster))
                current_cluster = [level]
        
        # Add the last cluster
        if current_cluster:
            clustered.append(sum(current_cluster) / len(current_cluster))
        
        return clustered


class SignalGenerator:
    """Generate trading signals based on technical analysis and ML predictions"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.sr_calculator = SupportResistanceCalculator()
    
    def generate_signals(
        self, 
        market_data: List[MarketData], 
        ml_prediction: Optional[Dict[str, Any]] = None,
        timeframe: str = "1D"
    ) -> Dict[str, Any]:
        """Generate comprehensive trading signals"""
        try:
            if len(market_data) < 20:
                raise ValueError("Insufficient data for signal generation")
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'timestamp': data.timestamp,
                'open_price': data.open_price,
                'high_price': data.high_price,
                'low_price': data.low_price,
                'close_price': data.close_price,
                'volume': data.volume
            } for data in market_data])
            
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Calculate technical indicators
            signals = self._calculate_technical_signals(df)
            
            # Calculate support and resistance
            sr_levels = self.sr_calculator.calculate_support_resistance(market_data)
            
            # Incorporate ML prediction if available
            if ml_prediction:
                signals.update(self._incorporate_ml_signals(df, ml_prediction))
            
            # Generate final signal
            final_signal = self._generate_final_signal(signals, sr_levels, df)
            
            # Add support/resistance levels
            final_signal.update(sr_levels)
            
            logger.info("Trading signals generated", 
                       signal_type=final_signal.get('signal_type'),
                       strength=final_signal.get('strength'))
            
            return final_signal
            
        except Exception as e:
            logger.error("Failed to generate signals", error=str(e))
            raise
    
    def _calculate_technical_signals(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate signals from technical indicators"""
        signals = {}
        
        try:
            # RSI signals
            rsi = self.indicators.rsi(df['close_price'])
            current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            if current_rsi > 70:
                signals['rsi_signal'] = 'SELL'
                signals['rsi_strength'] = min(1.0, (current_rsi - 70) / 30)
            elif current_rsi < 30:
                signals['rsi_signal'] = 'BUY'
                signals['rsi_strength'] = min(1.0, (30 - current_rsi) / 30)
            else:
                signals['rsi_signal'] = 'HOLD'
                signals['rsi_strength'] = 0.0
            
            # MACD signals
            macd_data = self.indicators.macd(df['close_price'])
            macd_line = macd_data['macd'].iloc[-1] if not pd.isna(macd_data['macd'].iloc[-1]) else 0
            signal_line = macd_data['signal'].iloc[-1] if not pd.isna(macd_data['signal'].iloc[-1]) else 0
            
            if macd_line > signal_line:
                signals['macd_signal'] = 'BUY'
                signals['macd_strength'] = min(1.0, abs(macd_line - signal_line) / abs(signal_line) if signal_line != 0 else 0.5)
            else:
                signals['macd_signal'] = 'SELL'
                signals['macd_strength'] = min(1.0, abs(signal_line - macd_line) / abs(signal_line) if signal_line != 0 else 0.5)
            
            # Moving Average signals
            sma_20 = self.indicators.sma(df['close_price'], 20).iloc[-1]
            sma_50 = self.indicators.sma(df['close_price'], 50).iloc[-1]
            current_price = df['close_price'].iloc[-1]
            
            if not pd.isna(sma_20) and not pd.isna(sma_50):
                if sma_20 > sma_50 and current_price > sma_20:
                    signals['ma_signal'] = 'BUY'
                    signals['ma_strength'] = min(1.0, (current_price - sma_20) / sma_20)
                elif sma_20 < sma_50 and current_price < sma_20:
                    signals['ma_signal'] = 'SELL'
                    signals['ma_strength'] = min(1.0, (sma_20 - current_price) / sma_20)
                else:
                    signals['ma_signal'] = 'HOLD'
                    signals['ma_strength'] = 0.0
            
            # Bollinger Bands signals
            bb_data = self.indicators.bollinger_bands(df['close_price'])
            upper_band = bb_data['upper'].iloc[-1]
            lower_band = bb_data['lower'].iloc[-1]
            
            if not pd.isna(upper_band) and not pd.isna(lower_band):
                if current_price > upper_band:
                    signals['bb_signal'] = 'SELL'
                    signals['bb_strength'] = min(1.0, (current_price - upper_band) / upper_band)
                elif current_price < lower_band:
                    signals['bb_signal'] = 'BUY'
                    signals['bb_strength'] = min(1.0, (lower_band - current_price) / lower_band)
                else:
                    signals['bb_signal'] = 'HOLD'
                    signals['bb_strength'] = 0.0
            
            # Volume analysis
            volume_sma = df['volume'].rolling(20).mean().iloc[-1]
            current_volume = df['volume'].iloc[-1]
            
            if current_volume > volume_sma * 1.5:
                signals['volume_confirmation'] = True
                signals['volume_strength'] = min(1.0, current_volume / volume_sma - 1)
            else:
                signals['volume_confirmation'] = False
                signals['volume_strength'] = 0.0
            
        except Exception as e:
            logger.error("Failed to calculate technical signals", error=str(e))
        
        return signals
    
    def _incorporate_ml_signals(self, df: pd.DataFrame, ml_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Incorporate ML prediction into signal generation"""
        ml_signals = {}
        
        try:
            predicted_price = ml_prediction.get('predicted_price', 0)
            current_price = df['close_price'].iloc[-1]
            confidence = ml_prediction.get('confidence_score', 0)
            
            if predicted_price > 0 and confidence > 0.5:
                price_change_pct = (predicted_price - current_price) / current_price
                
                if price_change_pct > 0.02:  # 2% upside
                    ml_signals['ml_signal'] = 'BUY'
                    ml_signals['ml_strength'] = min(1.0, confidence * abs(price_change_pct) * 10)
                elif price_change_pct < -0.02:  # 2% downside
                    ml_signals['ml_signal'] = 'SELL'
                    ml_signals['ml_strength'] = min(1.0, confidence * abs(price_change_pct) * 10)
                else:
                    ml_signals['ml_signal'] = 'HOLD'
                    ml_signals['ml_strength'] = 0.0
                
                ml_signals['ml_confidence'] = confidence
                ml_signals['ml_predicted_price'] = predicted_price
            
        except Exception as e:
            logger.error("Failed to incorporate ML signals", error=str(e))
        
        return ml_signals
    
    def _generate_final_signal(
        self, 
        signals: Dict[str, Any], 
        sr_levels: Dict[str, Any], 
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Generate final trading signal by combining all indicators"""
        try:
            current_price = df['close_price'].iloc[-1]
            
            # Collect individual signals
            buy_signals = []
            sell_signals = []
            
            signal_weights = {
                'rsi': 0.2,
                'macd': 0.25,
                'ma': 0.2,
                'bb': 0.15,
                'ml': 0.2
            }
            
            # Process each signal type
            for signal_type in ['rsi', 'macd', 'ma', 'bb', 'ml']:
                signal_key = f'{signal_type}_signal'
                strength_key = f'{signal_type}_strength'
                
                if signal_key in signals:
                    weight = signal_weights.get(signal_type, 0.1)
                    strength = signals.get(strength_key, 0.0)
                    weighted_strength = weight * strength
                    
                    if signals[signal_key] == 'BUY':
                        buy_signals.append(weighted_strength)
                    elif signals[signal_key] == 'SELL':
                        sell_signals.append(weighted_strength)
            
            # Calculate overall signal strength
            total_buy_strength = sum(buy_signals)
            total_sell_strength = sum(sell_signals)
            
            # Volume confirmation boost
            if signals.get('volume_confirmation', False):
                volume_boost = signals.get('volume_strength', 0) * 0.1
                if total_buy_strength > total_sell_strength:
                    total_buy_strength += volume_boost
                else:
                    total_sell_strength += volume_boost
            
            # Determine final signal
            if total_buy_strength > total_sell_strength and total_buy_strength > 0.3:
                signal_type = SignalTypeEnum.BUY
                signal_strength = min(1.0, total_buy_strength)
            elif total_sell_strength > total_buy_strength and total_sell_strength > 0.3:
                signal_type = SignalTypeEnum.SELL
                signal_strength = min(1.0, total_sell_strength)
            else:
                signal_type = SignalTypeEnum.HOLD
                signal_strength = 0.0
            
            # Calculate price targets and stop loss
            price_target, stop_loss = self._calculate_price_targets(
                current_price, signal_type, sr_levels, signal_strength
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(signals, signal_type, signal_strength)
            
            return {
                'signal_type': signal_type,
                'strength': round(signal_strength, 3),
                'price_target': price_target,
                'stop_loss': stop_loss,
                'reasoning': reasoning,
                'individual_signals': {
                    'buy_strength': round(total_buy_strength, 3),
                    'sell_strength': round(total_sell_strength, 3),
                    'technical_signals': signals
                }
            }
            
        except Exception as e:
            logger.error("Failed to generate final signal", error=str(e))
            return {
                'signal_type': SignalTypeEnum.HOLD,
                'strength': 0.0,
                'price_target': None,
                'stop_loss': None,
                'reasoning': 'Signal generation failed'
            }
    
    def _calculate_price_targets(
        self, 
        current_price: float, 
        signal_type: SignalTypeEnum, 
        sr_levels: Dict[str, Any], 
        strength: float
    ) -> Tuple[Optional[float], Optional[float]]:
        """Calculate price targets and stop loss levels"""
        try:
            if signal_type == SignalTypeEnum.HOLD:
                return None, None
            
            support_levels = sr_levels.get('support_levels', [])
            resistance_levels = sr_levels.get('resistance_levels', [])
            
            if signal_type == SignalTypeEnum.BUY:
                # Price target: next resistance or percentage-based
                if resistance_levels:
                    price_target = resistance_levels[0]
                else:
                    # Use strength-based target (1-5% upside)
                    target_pct = 0.01 + (strength * 0.04)
                    price_target = current_price * (1 + target_pct)
                
                # Stop loss: nearest support or percentage-based
                if support_levels:
                    stop_loss = support_levels[0]
                else:
                    # Conservative stop loss (2-5% downside)
                    stop_pct = 0.02 + (strength * 0.03)
                    stop_loss = current_price * (1 - stop_pct)
            
            else:  # SELL signal
                # Price target: next support or percentage-based
                if support_levels:
                    price_target = support_levels[0]
                else:
                    # Use strength-based target (1-5% downside)
                    target_pct = 0.01 + (strength * 0.04)
                    price_target = current_price * (1 - target_pct)
                
                # Stop loss: nearest resistance or percentage-based
                if resistance_levels:
                    stop_loss = resistance_levels[0]
                else:
                    # Conservative stop loss (2-5% upside)
                    stop_pct = 0.02 + (strength * 0.03)
                    stop_loss = current_price * (1 + stop_pct)
            
            return round(price_target, 2), round(stop_loss, 2)
            
        except Exception as e:
            logger.error("Failed to calculate price targets", error=str(e))
            return None, None
    
    def _generate_reasoning(
        self, 
        signals: Dict[str, Any], 
        signal_type: SignalTypeEnum, 
        strength: float
    ) -> str:
        """Generate human-readable reasoning for the signal"""
        try:
            reasons = []
            
            # Technical indicator reasons
            if signals.get('rsi_signal') == signal_type.value:
                rsi_strength = signals.get('rsi_strength', 0)
                if signal_type == SignalTypeEnum.BUY:
                    reasons.append(f"RSI indicates oversold conditions (strength: {rsi_strength:.2f})")
                else:
                    reasons.append(f"RSI indicates overbought conditions (strength: {rsi_strength:.2f})")
            
            if signals.get('macd_signal') == signal_type.value:
                reasons.append("MACD shows bullish momentum" if signal_type == SignalTypeEnum.BUY else "MACD shows bearish momentum")
            
            if signals.get('ma_signal') == signal_type.value:
                reasons.append("Moving averages support the trend")
            
            if signals.get('bb_signal') == signal_type.value:
                reasons.append("Bollinger Bands indicate potential reversal")
            
            if signals.get('ml_signal') == signal_type.value:
                ml_confidence = signals.get('ml_confidence', 0)
                reasons.append(f"ML model predicts favorable price movement (confidence: {ml_confidence:.2f})")
            
            if signals.get('volume_confirmation'):
                reasons.append("High volume confirms the signal")
            
            if not reasons:
                reasons.append("Mixed signals suggest holding position")
            
            # Add strength qualifier
            if strength > 0.7:
                strength_desc = "Strong"
            elif strength > 0.4:
                strength_desc = "Moderate"
            else:
                strength_desc = "Weak"
            
            reasoning = f"{strength_desc} {signal_type.value.lower()} signal. " + "; ".join(reasons)
            
            return reasoning[:500]  # Limit length
            
        except Exception as e:
            logger.error("Failed to generate reasoning", error=str(e))
            return f"{signal_type.value} signal generated"


class RiskManager:
    """Apply risk management rules to trading signals"""
    
    @staticmethod
    def apply_risk_filters(
        signal: Dict[str, Any], 
        market_data: List[MarketData],
        max_risk_per_trade: float = 0.02,
        max_position_size: float = 0.1
    ) -> Dict[str, Any]:
        """Apply risk management filters to signals"""
        try:
            filtered_signal = signal.copy()
            
            # Check market volatility
            if len(market_data) >= 20:
                recent_prices = [data.close_price for data in market_data[-20:]]
                volatility = np.std(recent_prices) / np.mean(recent_prices)
                
                # Reduce signal strength in high volatility
                if volatility > 0.05:  # 5% volatility threshold
                    volatility_factor = max(0.5, 1 - (volatility - 0.05) * 5)
                    filtered_signal['strength'] *= volatility_factor
                    filtered_signal['reasoning'] += f" (Adjusted for high volatility: {volatility:.3f})"
            
            # Adjust position size based on signal strength
            position_size = min(max_position_size, filtered_signal['strength'] * max_position_size)
            filtered_signal['recommended_position_size'] = round(position_size, 3)
            
            # Risk-reward ratio check
            current_price = market_data[-1].close_price
            price_target = filtered_signal.get('price_target')
            stop_loss = filtered_signal.get('stop_loss')
            
            if price_target and stop_loss:
                if filtered_signal['signal_type'] == SignalTypeEnum.BUY:
                    potential_gain = price_target - current_price
                    potential_loss = current_price - stop_loss
                else:
                    potential_gain = current_price - price_target
                    potential_loss = stop_loss - current_price
                
                if potential_loss > 0:
                    risk_reward_ratio = potential_gain / potential_loss
                    filtered_signal['risk_reward_ratio'] = round(risk_reward_ratio, 2)
                    
                    # Filter out signals with poor risk-reward ratio
                    if risk_reward_ratio < 1.5:
                        filtered_signal['strength'] *= 0.5
                        filtered_signal['reasoning'] += f" (Poor risk-reward ratio: {risk_reward_ratio:.2f})"
            
            # Final strength check
            if filtered_signal['strength'] < 0.2:
                filtered_signal['signal_type'] = SignalTypeEnum.HOLD
                filtered_signal['strength'] = 0.0
                filtered_signal['reasoning'] = "Signal filtered out due to risk management rules"
            
            return filtered_signal
            
        except Exception as e:
            logger.error("Failed to apply risk filters", error=str(e))
            return signal