"""
Machine Learning service for price predictions and model management
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import structlog

from app.ml.models import LSTMModel, RandomForestModel, SVRModel
from app.ml.feature_engineering import FeatureExtractor
from app.models.market_data import MarketData
from app.schemas.market_data import PredictionSchema, TimeHorizonEnum
from sqlalchemy.orm import Session

logger = structlog.get_logger()


class ModelManager:
    """Manages multiple ML models and their lifecycle"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.models = {}
        self.feature_extractor = FeatureExtractor()
        self.model_performance = {}
        
        # Ensure models directory exists
        os.makedirs(models_dir, exist_ok=True)
    
    def initialize_models(self) -> None:
        """Initialize all ML models"""
        try:
            # LSTM for time series prediction
            self.models['lstm_short'] = LSTMModel(sequence_length=60, features=1)
            self.models['lstm_medium'] = LSTMModel(sequence_length=120, features=1)
            self.models['lstm_long'] = LSTMModel(sequence_length=240, features=1)
            
            # Random Forest for pattern recognition
            self.models['rf_regression'] = RandomForestModel(task_type='regression')
            self.models['rf_classification'] = RandomForestModel(task_type='classification')
            
            # SVR for trend analysis
            self.models['svr_trend'] = SVRModel(kernel='rbf')
            
            logger.info("ML models initialized", models=list(self.models.keys()))
            
        except Exception as e:
            logger.error("Failed to initialize models", error=str(e))
            raise
    
    def prepare_data_for_training(self, market_data: List[MarketData]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Prepare market data for ML training"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame([{
                'timestamp': data.timestamp,
                'open_price': data.open_price,
                'high_price': data.high_price,
                'low_price': data.low_price,
                'close_price': data.close_price,
                'volume': data.volume
            } for data in market_data])
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Extract features
            features_df = self.feature_extractor.extract_features(df)
            
            # Create targets
            targets_df = self.feature_extractor.create_target_variables(df, horizons=[1, 5, 10])
            
            logger.info("Data prepared for training", 
                       records=len(df),
                       features=len(features_df.columns),
                       targets=len(targets_df.columns))
            
            return features_df, targets_df
            
        except Exception as e:
            logger.error("Failed to prepare training data", error=str(e))
            raise
    
    def train_models(self, market_data: List[MarketData], symbol: str) -> Dict[str, Any]:
        """Train all models with market data"""
        try:
            if not self.models:
                self.initialize_models()
            
            # Prepare data
            features_df, targets_df = self.prepare_data_for_training(market_data)
            
            # Remove NaN values
            combined_df = pd.concat([features_df, targets_df], axis=1).dropna()
            
            if len(combined_df) < 100:
                raise ValueError("Insufficient data for training (minimum 100 records required)")
            
            training_results = {}
            
            # Prepare data for different models
            feature_cols = [col for col in combined_df.columns if not col.startswith(('price_change_', 'direction_', 'volatility_'))]
            X = combined_df[feature_cols].values
            
            # Preprocess features
            X_processed, preprocessing_objects = self.feature_extractor.preprocess_features(
                combined_df[feature_cols], fit_scaler=True
            )
            
            # Train LSTM models
            price_data = combined_df['close_price'].values.reshape(-1, 1)
            
            for model_name in ['lstm_short', 'lstm_medium', 'lstm_long']:
                try:
                    model = self.models[model_name]
                    metrics = model.train(price_data, epochs=50, batch_size=32)
                    training_results[model_name] = metrics
                    
                    # Save model
                    model_path = os.path.join(self.models_dir, f"{symbol}_{model_name}")
                    model.save_model(model_path)
                    
                except Exception as e:
                    logger.error(f"Failed to train {model_name}", error=str(e))
                    training_results[model_name] = {'error': str(e)}
            
            # Train Random Forest models
            for target_horizon in [1, 5, 10]:
                # Regression target
                y_reg = combined_df[f'price_change_{target_horizon}'].values
                valid_indices = ~np.isnan(y_reg)
                
                if np.sum(valid_indices) > 50:
                    try:
                        model = RandomForestModel(task_type='regression')
                        metrics = model.train(X_processed.values[valid_indices], y_reg[valid_indices])
                        training_results[f'rf_regression_{target_horizon}'] = metrics
                        
                        # Save model
                        model_path = os.path.join(self.models_dir, f"{symbol}_rf_regression_{target_horizon}")
                        model.save_model(model_path)
                        
                    except Exception as e:
                        logger.error(f"Failed to train RF regression for horizon {target_horizon}", error=str(e))
                
                # Classification target
                y_class = combined_df[f'direction_{target_horizon}'].values
                valid_indices = ~np.isnan(y_class)
                
                if np.sum(valid_indices) > 50:
                    try:
                        model = RandomForestModel(task_type='classification')
                        metrics = model.train(X_processed.values[valid_indices], y_class[valid_indices])
                        training_results[f'rf_classification_{target_horizon}'] = metrics
                        
                        # Save model
                        model_path = os.path.join(self.models_dir, f"{symbol}_rf_classification_{target_horizon}")
                        model.save_model(model_path)
                        
                    except Exception as e:
                        logger.error(f"Failed to train RF classification for horizon {target_horizon}", error=str(e))
            
            # Train SVR model
            y_trend = combined_df['price_change_5'].values
            valid_indices = ~np.isnan(y_trend)
            
            if np.sum(valid_indices) > 50:
                try:
                    model = SVRModel()
                    metrics = model.train(X_processed.values[valid_indices], y_trend[valid_indices])
                    training_results['svr_trend'] = metrics
                    
                    # Save model
                    model_path = os.path.join(self.models_dir, f"{symbol}_svr_trend")
                    model.save_model(model_path)
                    
                except Exception as e:
                    logger.error("Failed to train SVR model", error=str(e))
                    training_results['svr_trend'] = {'error': str(e)}
            
            # Store performance metrics
            self.model_performance[symbol] = training_results
            
            logger.info("Model training completed", 
                       symbol=symbol,
                       models_trained=len([k for k, v in training_results.items() if 'error' not in v]))
            
            return training_results
            
        except Exception as e:
            logger.error("Failed to train models", symbol=symbol, error=str(e))
            raise


class PredictionEngine:
    """Engine for generating price predictions using trained models"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.model_manager = ModelManager(models_dir)
        self.feature_extractor = FeatureExtractor()
    
    def generate_prediction(
        self, 
        market_data: List[MarketData], 
        symbol: str, 
        timeframe: str, 
        time_horizon: str = "short"
    ) -> Dict[str, Any]:
        """Generate price prediction using ensemble of models"""
        try:
            if len(market_data) < 60:
                raise ValueError("Insufficient data for prediction (minimum 60 records required)")
            
            # Prepare data
            df = pd.DataFrame([{
                'timestamp': data.timestamp,
                'open_price': data.open_price,
                'high_price': data.high_price,
                'low_price': data.low_price,
                'close_price': data.close_price,
                'volume': data.volume
            } for data in market_data])
            
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Extract features
            features_df = self.feature_extractor.extract_features(df)
            
            # Get latest features for prediction
            latest_features = features_df.iloc[-1:].select_dtypes(include=[np.number])
            
            # Preprocess features
            X_processed, _ = self.feature_extractor.preprocess_features(latest_features, fit_scaler=False)
            
            predictions = {}
            confidence_scores = {}
            
            # Current price
            current_price = df['close_price'].iloc[-1]
            
            # Generate predictions from different models
            try:
                # LSTM prediction
                lstm_model_name = f"lstm_{time_horizon}"
                if lstm_model_name in self.model_manager.models:
                    price_data = df['close_price'].values.reshape(-1, 1)
                    lstm_pred = self.model_manager.models[lstm_model_name].predict(price_data)
                    if len(lstm_pred) > 0:
                        predictions['lstm'] = lstm_pred[-1]
                        confidence_scores['lstm'] = 0.7  # Base confidence
                
            except Exception as e:
                logger.warning("LSTM prediction failed", error=str(e))
            
            try:
                # Random Forest prediction
                horizon_map = {'short': 1, 'medium': 5, 'long': 10}
                horizon = horizon_map.get(time_horizon, 1)
                
                rf_model = RandomForestModel(task_type='regression')
                model_path = os.path.join(self.models_dir, f"{symbol}_rf_regression_{horizon}")
                
                if os.path.exists(f"{model_path}_rf_regression.pkl"):
                    rf_model.load_model(model_path)
                    rf_pred = rf_model.predict(X_processed.values)
                    
                    # Convert price change to actual price
                    predicted_price = current_price * (1 + rf_pred[0])
                    predictions['random_forest'] = predicted_price
                    confidence_scores['random_forest'] = 0.8
                
            except Exception as e:
                logger.warning("Random Forest prediction failed", error=str(e))
            
            try:
                # SVR prediction
                svr_model = SVRModel()
                model_path = os.path.join(self.models_dir, f"{symbol}_svr_trend")
                
                if os.path.exists(f"{model_path}_svr.pkl"):
                    svr_model.load_model(model_path)
                    svr_pred = svr_model.predict(X_processed.values)
                    
                    # Convert price change to actual price
                    predicted_price = current_price * (1 + svr_pred[0])
                    predictions['svr'] = predicted_price
                    confidence_scores['svr'] = 0.6
                
            except Exception as e:
                logger.warning("SVR prediction failed", error=str(e))
            
            # Ensemble prediction
            if predictions:
                # Weighted average based on confidence scores
                total_weight = sum(confidence_scores.values())
                ensemble_prediction = sum(
                    pred * confidence_scores[model] / total_weight 
                    for model, pred in predictions.items()
                )
                
                # Calculate overall confidence
                overall_confidence = min(0.95, sum(confidence_scores.values()) / len(confidence_scores))
                
            else:
                # Fallback: simple trend-based prediction
                recent_prices = df['close_price'].tail(5)
                trend = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0]
                ensemble_prediction = current_price * (1 + trend * 0.1)  # Conservative trend extrapolation
                overall_confidence = 0.3
            
            result = {
                'predicted_price': round(ensemble_prediction, 2),
                'current_price': round(current_price, 2),
                'price_change_percent': round(((ensemble_prediction - current_price) / current_price) * 100, 2),
                'confidence_score': round(overall_confidence, 3),
                'time_horizon': time_horizon,
                'timeframe': timeframe,
                'model_predictions': predictions,
                'model_confidences': confidence_scores,
                'prediction_timestamp': datetime.now()
            }
            
            logger.info("Prediction generated successfully", 
                       symbol=symbol,
                       predicted_price=ensemble_prediction,
                       confidence=overall_confidence)
            
            return result
            
        except Exception as e:
            logger.error("Failed to generate prediction", symbol=symbol, error=str(e))
            raise
    
    def calculate_confidence(self, predictions: Dict[str, float], historical_accuracy: Dict[str, float] = None) -> float:
        """Calculate prediction confidence based on model agreement and historical accuracy"""
        try:
            if not predictions:
                return 0.0
            
            # Model agreement (how close predictions are to each other)
            pred_values = list(predictions.values())
            if len(pred_values) > 1:
                std_dev = np.std(pred_values)
                mean_pred = np.mean(pred_values)
                agreement_score = max(0, 1 - (std_dev / mean_pred))
            else:
                agreement_score = 0.5
            
            # Historical accuracy (if available)
            if historical_accuracy:
                avg_accuracy = np.mean(list(historical_accuracy.values()))
                confidence = (agreement_score * 0.6) + (avg_accuracy * 0.4)
            else:
                confidence = agreement_score * 0.8  # Lower confidence without historical data
            
            return min(0.95, max(0.1, confidence))  # Clamp between 0.1 and 0.95
            
        except Exception as e:
            logger.error("Failed to calculate confidence", error=str(e))
            return 0.5
    
    def update_model_performance(self, symbol: str, actual_price: float, predicted_price: float, model_name: str) -> None:
        """Update model performance tracking"""
        try:
            if symbol not in self.model_manager.model_performance:
                self.model_manager.model_performance[symbol] = {}
            
            if model_name not in self.model_manager.model_performance[symbol]:
                self.model_manager.model_performance[symbol][model_name] = {
                    'predictions': [],
                    'accuracy_scores': []
                }
            
            # Calculate accuracy (percentage error)
            error = abs(actual_price - predicted_price) / actual_price
            accuracy = max(0, 1 - error)
            
            # Store performance data
            perf_data = self.model_manager.model_performance[symbol][model_name]
            perf_data['predictions'].append({
                'predicted': predicted_price,
                'actual': actual_price,
                'accuracy': accuracy,
                'timestamp': datetime.now()
            })
            perf_data['accuracy_scores'].append(accuracy)
            
            # Keep only last 100 predictions
            if len(perf_data['predictions']) > 100:
                perf_data['predictions'] = perf_data['predictions'][-100:]
                perf_data['accuracy_scores'] = perf_data['accuracy_scores'][-100:]
            
            logger.info("Model performance updated", 
                       symbol=symbol,
                       model=model_name,
                       accuracy=accuracy)
            
        except Exception as e:
            logger.error("Failed to update model performance", error=str(e))
    
    def get_model_performance_stats(self, symbol: str) -> Dict[str, Any]:
        """Get performance statistics for all models"""
        try:
            if symbol not in self.model_manager.model_performance:
                return {}
            
            stats = {}
            for model_name, perf_data in self.model_manager.model_performance[symbol].items():
                if perf_data['accuracy_scores']:
                    stats[model_name] = {
                        'avg_accuracy': np.mean(perf_data['accuracy_scores']),
                        'std_accuracy': np.std(perf_data['accuracy_scores']),
                        'min_accuracy': np.min(perf_data['accuracy_scores']),
                        'max_accuracy': np.max(perf_data['accuracy_scores']),
                        'total_predictions': len(perf_data['accuracy_scores'])
                    }
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get performance stats", error=str(e))
            return {}