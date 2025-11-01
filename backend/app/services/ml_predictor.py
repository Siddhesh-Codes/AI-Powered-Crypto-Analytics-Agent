"""
ML Prediction Service - Wrapper for using trained ML models
Integrates the LLM model's RandomForest/GradientBoosting predictions
"""

import sys
import os
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

# Add llm-model directory to path
BACKEND_DIR = Path(__file__).parent.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
LLM_MODEL_DIR = PROJECT_ROOT / "llm-model"
sys.path.insert(0, str(LLM_MODEL_DIR))

try:
    from ml_model import CryptoMLModel
    from data_preprocessor import LSTMDataPreprocessor
    print("✅ Successfully imported LLM model classes")
except ImportError as e:
    print(f"⚠️ Warning: Could not import LLM model classes: {e}")
    CryptoMLModel = None
    LSTMDataPreprocessor = None


class MLPredictionService:
    """
    Service for making predictions using trained ML models
    """
    
    def __init__(self):
        """Initialize ML prediction service"""
        self.model = None
        self.preprocessor = None
        self.model_path = LLM_MODEL_DIR / "models"
        self.model_loaded = False
        self.model_info = {}
        
    def load_latest_model(self) -> bool:
        """
        Load the most recent trained model
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            if not self.model_path.exists():
                print(f"⚠️ Model directory not found: {self.model_path}")
                return False
            
            # Find latest model file
            model_files = list(self.model_path.glob("ml_model_*.pkl"))
            
            if not model_files:
                print("⚠️ No trained models found. Please train a model first.")
                return False
            
            # Get most recent model
            latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
            
            # Load model
            self.model = joblib.load(latest_model)
            print(f"✅ Loaded model: {latest_model.name}")
            
            # Try to load model info
            info_file = latest_model.with_suffix('.json')
            if info_file.exists():
                with open(info_file, 'r') as f:
                    self.model_info = json.load(f)
                print(f"✅ Loaded model info: {self.model_info.get('model_type', 'unknown')}")
            
            self.model_loaded = True
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def prepare_features(self, crypto_data: pd.DataFrame) -> Optional[np.ndarray]:
        """
        Prepare features from crypto data for prediction
        
        Args:
            crypto_data: DataFrame with crypto price history
            
        Returns:
            Feature array ready for prediction
        """
        try:
            # Calculate technical indicators
            df = crypto_data.copy()
            
            # Price changes
            df['price_change'] = df['close'].pct_change()
            df['price_change_2d'] = df['close'].pct_change(periods=2)
            df['price_change_7d'] = df['close'].pct_change(periods=7)
            
            # Moving averages
            df['ma_7'] = df['close'].rolling(window=7).mean()
            df['ma_14'] = df['close'].rolling(window=14).mean()
            df['ma_30'] = df['close'].rolling(window=30).mean()
            
            # Volatility
            df['volatility_7d'] = df['close'].rolling(window=7).std()
            df['volatility_30d'] = df['close'].rolling(window=30).mean()
            
            # Volume indicators
            if 'volume' in df.columns:
                df['volume_change'] = df['volume'].pct_change()
                df['volume_ma_7'] = df['volume'].rolling(window=7).mean()
            
            # RSI (Relative Strength Index)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Drop NaN values
            df = df.dropna()
            
            if len(df) == 0:
                print("⚠️ No valid data after feature engineering")
                return None
            
            # Select features
            feature_columns = [
                'close', 'price_change', 'price_change_2d', 'price_change_7d',
                'ma_7', 'ma_14', 'ma_30', 'volatility_7d', 'volatility_30d', 'rsi'
            ]
            
            if 'volume' in df.columns:
                feature_columns.extend(['volume_change', 'volume_ma_7'])
            
            # Get the latest row for prediction
            features = df[feature_columns].iloc[-1:].values
            
            return features
            
        except Exception as e:
            print(f"❌ Error preparing features: {e}")
            return None
    
    def predict_price(self, crypto_symbol: str, crypto_data: pd.DataFrame, 
                     days_ahead: int = 7) -> Optional[Dict]:
        """
        Predict future price for a cryptocurrency
        
        Args:
            crypto_symbol: Symbol of the cryptocurrency (e.g., 'BTC')
            crypto_data: Historical price data
            days_ahead: Number of days to predict ahead
            
        Returns:
            Dictionary with prediction results
        """
        try:
            # Load model if not loaded
            if not self.model_loaded:
                if not self.load_latest_model():
                    return {
                        'success': False,
                        'error': 'Model not loaded. Please train a model first.',
                        'predictions': None
                    }
            
            # Prepare features
            features = self.prepare_features(crypto_data)
            
            if features is None:
                return {
                    'success': False,
                    'error': 'Failed to prepare features',
                    'predictions': None
                }
            
            # Make prediction
            prediction = self.model.predict(features)[0]
            
            # Get current price
            current_price = crypto_data['close'].iloc[-1]
            
            # Calculate prediction statistics
            price_change = prediction - current_price
            price_change_pct = (price_change / current_price) * 100
            
            # Determine trend
            if price_change_pct > 2:
                trend = "bullish"
                confidence = min(abs(price_change_pct) * 5, 95)
            elif price_change_pct < -2:
                trend = "bearish"
                confidence = min(abs(price_change_pct) * 5, 95)
            else:
                trend = "neutral"
                confidence = 60
            
            # Create prediction result
            result = {
                'success': True,
                'symbol': crypto_symbol,
                'current_price': float(current_price),
                'predicted_price': float(prediction),
                'price_change': float(price_change),
                'price_change_pct': float(price_change_pct),
                'trend': trend,
                'confidence': float(confidence),
                'days_ahead': days_ahead,
                'prediction_date': (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d'),
                'model_type': self.model_info.get('model_type', 'ML Model'),
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error making prediction: {e}")
            return {
                'success': False,
                'error': str(e),
                'predictions': None
            }
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        if not self.model_loaded:
            return {
                'loaded': False,
                'message': 'No model loaded'
            }
        
        return {
            'loaded': True,
            'model_type': self.model_info.get('model_type', 'Unknown'),
            'training_date': self.model_info.get('training_date', 'Unknown'),
            'accuracy': self.model_info.get('test_score', 'Unknown'),
            'features': self.model_info.get('num_features', 'Unknown')
        }


# Global instance
ml_predictor = MLPredictionService()

# Try to load model on initialization
try:
    ml_predictor.load_latest_model()
except Exception as e:
    print(f"⚠️ Could not load model on initialization: {e}")
