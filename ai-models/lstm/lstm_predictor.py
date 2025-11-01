import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib
import logging
from typing import Tuple, Optional

class LSTMPricePredictor:
    """
    LSTM Neural Network for Cryptocurrency Price Prediction
    
    This class implements a Long Short-Term Memory (LSTM) neural network
    specifically designed for predicting cryptocurrency prices using time series data.
    """
    
    def __init__(self, 
                 sequence_length: int = 60,
                 lstm_units: int = 50,
                 dropout_rate: float = 0.2,
                 epochs: int = 100,
                 batch_size: int = 32):
        """
        Initialize LSTM Price Predictor
        
        Args:
            sequence_length: Number of time steps to look back
            lstm_units: Number of LSTM units in each layer
            dropout_rate: Dropout rate for regularization
            epochs: Number of training epochs
            batch_size: Batch size for training
        """
        self.sequence_length = sequence_length
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.epochs = epochs
        self.batch_size = batch_size
        
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.is_trained = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _create_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """
        Create LSTM model architecture
        
        Args:
            input_shape: Shape of input data (sequence_length, features)
            
        Returns:
            Compiled LSTM model
        """
        model = Sequential()
        
        # First LSTM layer
        model.add(LSTM(units=self.lstm_units, 
                      return_sequences=True, 
                      input_shape=input_shape))
        model.add(Dropout(self.dropout_rate))
        
        # Second LSTM layer
        model.add(LSTM(units=self.lstm_units, 
                      return_sequences=True))
        model.add(Dropout(self.dropout_rate))
        
        # Third LSTM layer
        model.add(LSTM(units=self.lstm_units))
        model.add(Dropout(self.dropout_rate))
        
        # Output layer
        model.add(Dense(units=1))
        
        # Compile model
        model.compile(optimizer=Adam(learning_rate=0.001),
                     loss='mean_squared_error',
                     metrics=['mae'])
        
        return model
    
    def _prepare_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare sequences for LSTM training
        
        Args:
            data: Scaled price data
            
        Returns:
            X: Input sequences
            y: Target values
        """
        X, y = [], []
        
        for i in range(self.sequence_length, len(data)):
            X.append(data[i-self.sequence_length:i, 0])
            y.append(data[i, 0])
        
        return np.array(X), np.array(y)
    
    def train(self, price_data: pd.DataFrame, 
              price_column: str = 'close',
              validation_split: float = 0.2) -> dict:
        """
        Train the LSTM model
        
        Args:
            price_data: DataFrame containing price data
            price_column: Column name for price data
            validation_split: Fraction of data to use for validation
            
        Returns:
            Training history and metrics
        """
        try:
            self.logger.info("Starting LSTM model training...")
            
            # Prepare data
            prices = price_data[price_column].values.reshape(-1, 1)
            scaled_prices = self.scaler.fit_transform(prices)
            
            # Create sequences
            X, y = self._prepare_sequences(scaled_prices)
            
            # Reshape for LSTM input
            X = np.reshape(X, (X.shape[0], X.shape[1], 1))
            
            # Split data
            split_idx = int(len(X) * (1 - validation_split))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Create and train model
            self.model = self._create_model((X.shape[1], 1))
            
            # Training callbacks
            callbacks = [
                tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
                tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5)
            ]
            
            history = self.model.fit(
                X_train, y_train,
                epochs=self.epochs,
                batch_size=self.batch_size,
                validation_data=(X_val, y_val),
                callbacks=callbacks,
                verbose=1
            )
            
            # Calculate metrics
            train_pred = self.model.predict(X_train)
            val_pred = self.model.predict(X_val)
            
            train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
            val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
            
            train_mae = mean_absolute_error(y_train, train_pred)
            val_mae = mean_absolute_error(y_val, val_pred)
            
            self.is_trained = True
            
            metrics = {
                'train_rmse': float(train_rmse),
                'val_rmse': float(val_rmse),
                'train_mae': float(train_mae),
                'val_mae': float(val_mae),
                'final_loss': float(history.history['loss'][-1]),
                'final_val_loss': float(history.history['val_loss'][-1])
            }
            
            self.logger.info(f"Training completed. Validation RMSE: {val_rmse:.4f}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error during training: {str(e)}")
            raise
    
    def predict(self, recent_prices: np.ndarray, 
                steps_ahead: int = 1) -> np.ndarray:
        """
        Make price predictions
        
        Args:
            recent_prices: Recent price data for prediction
            steps_ahead: Number of steps to predict ahead
            
        Returns:
            Predicted prices
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            # Scale recent prices
            scaled_prices = self.scaler.transform(recent_prices.reshape(-1, 1))
            
            predictions = []
            current_sequence = scaled_prices[-self.sequence_length:].flatten()
            
            for _ in range(steps_ahead):
                # Reshape for model input
                X = current_sequence.reshape(1, self.sequence_length, 1)
                
                # Make prediction
                pred_scaled = self.model.predict(X)[0, 0]
                
                # Update sequence
                current_sequence = np.append(current_sequence[1:], pred_scaled)
                
                # Inverse transform prediction
                pred_price = self.scaler.inverse_transform([[pred_scaled]])[0, 0]
                predictions.append(pred_price)
            
            return np.array(predictions)
            
        except Exception as e:
            self.logger.error(f"Error during prediction: {str(e)}")
            raise
    
    def save_model(self, model_path: str, scaler_path: str):
        """Save trained model and scaler"""
        if not self.is_trained:
            raise ValueError("No trained model to save")
        
        self.model.save(model_path)
        joblib.dump(self.scaler, scaler_path)
        self.logger.info(f"Model saved to {model_path}")
    
    def load_model(self, model_path: str, scaler_path: str):
        """Load trained model and scaler"""
        self.model = tf.keras.models.load_model(model_path)
        self.scaler = joblib.load(scaler_path)
        self.is_trained = True
        self.logger.info(f"Model loaded from {model_path}")
    
    def get_model_summary(self) -> str:
        """Get model architecture summary"""
        if self.model is None:
            return "Model not created yet"
        
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            self.model.summary()
        return f.getvalue()


# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.02)
    
    sample_data = pd.DataFrame({
        'date': dates,
        'close': prices
    })
    
    # Test LSTM predictor
    predictor = LSTMPricePredictor(sequence_length=30, epochs=10)
    
    # Train model
    metrics = predictor.train(sample_data)
    print("Training Metrics:", metrics)
    
    # Make predictions
    recent_data = sample_data['close'].values[-60:]
    predictions = predictor.predict(recent_data, steps_ahead=7)
    print("7-day predictions:", predictions)
