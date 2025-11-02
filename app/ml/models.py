"""
Machine Learning models for price prediction
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import pickle
import joblib
from datetime import datetime
import structlog

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.svm import SVR, SVC
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score, classification_report
from sklearn.model_selection import train_test_split, cross_val_score

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

logger = structlog.get_logger()


class LSTMModel:
    """LSTM Neural Network for time series prediction"""
    
    def __init__(self, sequence_length: int = 60, features: int = 1):
        self.sequence_length = sequence_length
        self.features = features
        self.model = None
        self.scaler = None
        self.is_trained = False
    
    def build_model(self, lstm_units: List[int] = [50, 50], dropout_rate: float = 0.2) -> None:
        """Build LSTM model architecture"""
        try:
            self.model = keras.Sequential()
            
            # First LSTM layer
            self.model.add(layers.LSTM(
                lstm_units[0],
                return_sequences=True if len(lstm_units) > 1 else False,
                input_shape=(self.sequence_length, self.features)
            ))
            self.model.add(layers.Dropout(dropout_rate))
            
            # Additional LSTM layers
            for i, units in enumerate(lstm_units[1:], 1):
                return_seq = i < len(lstm_units) - 1
                self.model.add(layers.LSTM(units, return_sequences=return_seq))
                self.model.add(layers.Dropout(dropout_rate))
            
            # Dense layers
            self.model.add(layers.Dense(25, activation='relu'))
            self.model.add(layers.Dropout(dropout_rate))
            self.model.add(layers.Dense(1))
            
            # Compile model
            self.model.compile(
                optimizer='adam',
                loss='mse',
                metrics=['mae']
            )
            
            logger.info("LSTM model built successfully", 
                       sequence_length=self.sequence_length,
                       features=self.features,
                       lstm_units=lstm_units)
            
        except Exception as e:
            logger.error("Failed to build LSTM model", error=str(e))
            raise
    
    def prepare_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for LSTM training"""
        try:
            X, y = [], []
            
            for i in range(self.sequence_length, len(data)):
                X.append(data[i-self.sequence_length:i])
                y.append(data[i])
            
            return np.array(X), np.array(y)
            
        except Exception as e:
            logger.error("Failed to prepare sequences", error=str(e))
            raise
    
    def train(self, data: np.ndarray, validation_split: float = 0.2, epochs: int = 50, batch_size: int = 32) -> Dict[str, Any]:
        """Train LSTM model"""
        try:
            if self.model is None:
                self.build_model()
            
            # Prepare sequences
            X, y = self.prepare_sequences(data)
            
            # Split data
            split_idx = int(len(X) * (1 - validation_split))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Train model
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=batch_size,
                verbose=0
            )
            
            self.is_trained = True
            
            # Calculate metrics
            train_pred = self.model.predict(X_train)
            val_pred = self.model.predict(X_val)
            
            metrics = {
                'train_mse': mean_squared_error(y_train, train_pred),
                'val_mse': mean_squared_error(y_val, val_pred),
                'train_mae': mean_absolute_error(y_train, train_pred),
                'val_mae': mean_absolute_error(y_val, val_pred),
                'history': history.history
            }
            
            logger.info("LSTM model trained successfully", 
                       train_samples=len(X_train),
                       val_samples=len(X_val),
                       epochs=epochs)
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to train LSTM model", error=str(e))
            raise
    
    def predict(self, data: np.ndarray) -> np.ndarray:
        """Make predictions with LSTM model"""
        try:
            if not self.is_trained or self.model is None:
                raise ValueError("Model must be trained before making predictions")
            
            # Prepare sequences
            X, _ = self.prepare_sequences(data)
            
            # Make predictions
            predictions = self.model.predict(X)
            
            return predictions.flatten()
            
        except Exception as e:
            logger.error("Failed to make LSTM predictions", error=str(e))
            raise
    
    def save_model(self, filepath: str) -> None:
        """Save LSTM model"""
        try:
            if self.model is not None:
                self.model.save(f"{filepath}_lstm.h5")
                
                # Save metadata
                metadata = {
                    'sequence_length': self.sequence_length,
                    'features': self.features,
                    'is_trained': self.is_trained
                }
                
                with open(f"{filepath}_lstm_metadata.pkl", 'wb') as f:
                    pickle.dump(metadata, f)
                
                logger.info("LSTM model saved", filepath=filepath)
                
        except Exception as e:
            logger.error("Failed to save LSTM model", error=str(e))
            raise
    
    def load_model(self, filepath: str) -> None:
        """Load LSTM model"""
        try:
            # Load model
            self.model = keras.models.load_model(f"{filepath}_lstm.h5")
            
            # Load metadata
            with open(f"{filepath}_lstm_metadata.pkl", 'rb') as f:
                metadata = pickle.load(f)
            
            self.sequence_length = metadata['sequence_length']
            self.features = metadata['features']
            self.is_trained = metadata['is_trained']
            
            logger.info("LSTM model loaded", filepath=filepath)
            
        except Exception as e:
            logger.error("Failed to load LSTM model", error=str(e))
            raise


class RandomForestModel:
    """Random Forest model for price prediction and classification"""
    
    def __init__(self, task_type: str = 'regression'):
        self.task_type = task_type  # 'regression' or 'classification'
        self.model = None
        self.is_trained = False
        
        if task_type == 'regression':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
        else:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
    
    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2) -> Dict[str, Any]:
        """Train Random Forest model"""
        try:
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, random_state=42
            )
            
            # Train model
            self.model.fit(X_train, y_train)
            self.is_trained = True
            
            # Make predictions
            train_pred = self.model.predict(X_train)
            val_pred = self.model.predict(X_val)
            
            # Calculate metrics
            if self.task_type == 'regression':
                metrics = {
                    'train_mse': mean_squared_error(y_train, train_pred),
                    'val_mse': mean_squared_error(y_val, val_pred),
                    'train_mae': mean_absolute_error(y_train, train_pred),
                    'val_mae': mean_absolute_error(y_val, val_pred),
                    'feature_importance': self.model.feature_importances_
                }
            else:
                metrics = {
                    'train_accuracy': accuracy_score(y_train, train_pred),
                    'val_accuracy': accuracy_score(y_val, val_pred),
                    'classification_report': classification_report(y_val, val_pred, output_dict=True),
                    'feature_importance': self.model.feature_importances_
                }
            
            logger.info("Random Forest model trained successfully",
                       task_type=self.task_type,
                       train_samples=len(X_train),
                       val_samples=len(X_val))
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to train Random Forest model", error=str(e))
            raise
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions with Random Forest model"""
        try:
            if not self.is_trained:
                raise ValueError("Model must be trained before making predictions")
            
            return self.model.predict(X)
            
        except Exception as e:
            logger.error("Failed to make Random Forest predictions", error=str(e))
            raise
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities (classification only)"""
        try:
            if self.task_type != 'classification':
                raise ValueError("Probability predictions only available for classification")
            
            if not self.is_trained:
                raise ValueError("Model must be trained before making predictions")
            
            return self.model.predict_proba(X)
            
        except Exception as e:
            logger.error("Failed to get prediction probabilities", error=str(e))
            raise
    
    def get_feature_importance(self) -> np.ndarray:
        """Get feature importance scores"""
        if not self.is_trained:
            raise ValueError("Model must be trained to get feature importance")
        
        return self.model.feature_importances_
    
    def save_model(self, filepath: str) -> None:
        """Save Random Forest model"""
        try:
            joblib.dump(self.model, f"{filepath}_rf_{self.task_type}.pkl")
            
            metadata = {
                'task_type': self.task_type,
                'is_trained': self.is_trained
            }
            
            with open(f"{filepath}_rf_metadata.pkl", 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info("Random Forest model saved", filepath=filepath, task_type=self.task_type)
            
        except Exception as e:
            logger.error("Failed to save Random Forest model", error=str(e))
            raise
    
    def load_model(self, filepath: str) -> None:
        """Load Random Forest model"""
        try:
            self.model = joblib.load(f"{filepath}_rf_{self.task_type}.pkl")
            
            with open(f"{filepath}_rf_metadata.pkl", 'rb') as f:
                metadata = pickle.load(f)
            
            self.task_type = metadata['task_type']
            self.is_trained = metadata['is_trained']
            
            logger.info("Random Forest model loaded", filepath=filepath, task_type=self.task_type)
            
        except Exception as e:
            logger.error("Failed to load Random Forest model", error=str(e))
            raise


class SVRModel:
    """Support Vector Regression model for trend analysis"""
    
    def __init__(self, kernel: str = 'rbf'):
        self.kernel = kernel
        self.model = SVR(kernel=kernel, C=1.0, gamma='scale')
        self.is_trained = False
    
    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2) -> Dict[str, Any]:
        """Train SVR model"""
        try:
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, random_state=42
            )
            
            # Train model
            self.model.fit(X_train, y_train)
            self.is_trained = True
            
            # Make predictions
            train_pred = self.model.predict(X_train)
            val_pred = self.model.predict(X_val)
            
            # Calculate metrics
            metrics = {
                'train_mse': mean_squared_error(y_train, train_pred),
                'val_mse': mean_squared_error(y_val, val_pred),
                'train_mae': mean_absolute_error(y_train, train_pred),
                'val_mae': mean_absolute_error(y_val, val_pred)
            }
            
            logger.info("SVR model trained successfully",
                       kernel=self.kernel,
                       train_samples=len(X_train),
                       val_samples=len(X_val))
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to train SVR model", error=str(e))
            raise
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions with SVR model"""
        try:
            if not self.is_trained:
                raise ValueError("Model must be trained before making predictions")
            
            return self.model.predict(X)
            
        except Exception as e:
            logger.error("Failed to make SVR predictions", error=str(e))
            raise
    
    def save_model(self, filepath: str) -> None:
        """Save SVR model"""
        try:
            joblib.dump(self.model, f"{filepath}_svr.pkl")
            
            metadata = {
                'kernel': self.kernel,
                'is_trained': self.is_trained
            }
            
            with open(f"{filepath}_svr_metadata.pkl", 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info("SVR model saved", filepath=filepath, kernel=self.kernel)
            
        except Exception as e:
            logger.error("Failed to save SVR model", error=str(e))
            raise
    
    def load_model(self, filepath: str) -> None:
        """Load SVR model"""
        try:
            self.model = joblib.load(f"{filepath}_svr.pkl")
            
            with open(f"{filepath}_svr_metadata.pkl", 'rb') as f:
                metadata = pickle.load(f)
            
            self.kernel = metadata['kernel']
            self.is_trained = metadata['is_trained']
            
            logger.info("SVR model loaded", filepath=filepath, kernel=self.kernel)
            
        except Exception as e:
            logger.error("Failed to load SVR model", error=str(e))
            raise