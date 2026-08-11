"""
Data Preprocessor - Prepare data for LSTM training
Handles feature engineering, normalization, and sequence creation
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

class LSTMDataPreprocessor:
    """Preprocess time series data for LSTM model"""
    
    def __init__(self, sequence_length=14, forecast_horizon=1):
        """
        Args:
            sequence_length: Number of days to look back (input window)
            forecast_horizon: Number of days to predict ahead
        """
        self.sequence_length = sequence_length
        self.forecast_horizon = forecast_horizon
        self.price_scaler = MinMaxScaler()
        self.volume_scaler = MinMaxScaler()
        self.feature_scalers = {}
        
    def prepare_data(self, df):
        """
        Prepare data for LSTM training
        
        Args:
            df: DataFrame with columns [date, symbol, open, high, low, close, volume]
            
        Returns:
            X_train, X_test, y_train, y_test, scalers
        """
        print("\n" + "="*70)
        print("🔧 DATA PREPROCESSING FOR LSTM")
        print("="*70 + "\n")
        
        print(f"📊 Input data shape: {df.shape}")
        print(f"   Unique symbols: {df['symbol'].nunique()}")
        print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
        
        # Engineer features
        print("\n⚙️  Engineering features...")
        df_features = self._engineer_features(df)
        
        # Create sequences per symbol
        print("⚙️  Creating sequences...")
        X, y, symbols = self._create_sequences(df_features)
        
        print(f"\n✅ Created {len(X)} sequences")
        print(f"   Sequence shape: {X[0].shape if len(X) > 0 else 'N/A'}")
        print(f"   Target shape: {y[0].shape if len(y) > 0 else 'N/A'}")
        
        # Split train/test
        test_size = 0.2
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False, random_state=42
        )
        
        print(f"\n📊 Train/Test Split ({int((1-test_size)*100)}%/{int(test_size*100)}%):")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Testing samples: {len(X_test)}")
        
        return X_train, X_test, y_train, y_test
    
    def _engineer_features(self, df):
        """Engineer technical indicators and features"""
        df = df.copy()
        df = df.sort_values(['symbol', 'date']).reset_index(drop=True)
        
        features_list = []
        
        for symbol in df['symbol'].unique():
            symbol_df = df[df['symbol'] == symbol].copy()
            
            # Price-based features
            symbol_df['price_change'] = symbol_df['close'].pct_change()
            symbol_df['price_range'] = (symbol_df['high'] - symbol_df['low']) / symbol_df['close']
            
            # Moving averages
            symbol_df['ma_7'] = symbol_df['close'].rolling(window=7, min_periods=1).mean()
            symbol_df['ma_14'] = symbol_df['close'].rolling(window=14, min_periods=1).mean()
            
            # Volatility
            symbol_df['volatility'] = symbol_df['close'].rolling(window=7, min_periods=1).std()
            
            # RSI (Relative Strength Index)
            symbol_df['rsi'] = self._calculate_rsi(symbol_df['close'])
            
            # Volume features
            symbol_df['volume_change'] = symbol_df['volume'].pct_change()
            
            features_list.append(symbol_df)
        
        df_features = pd.concat(features_list, ignore_index=True)
        
        # Fill NaN values
        df_features = df_features.fillna(method='bfill').fillna(0)
        
        return df_features
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
        
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _create_sequences(self, df):
        """Create sequences for LSTM input"""
        feature_columns = ['close', 'volume', 'price_change', 'price_range', 
                          'ma_7', 'ma_14', 'volatility', 'rsi', 'volume_change']
        
        X, y, symbols = [], [], []
        
        for symbol in df['symbol'].unique():
            symbol_df = df[df['symbol'] == symbol].copy()
            
            # Normalize features per symbol
            symbol_features = symbol_df[feature_columns].values
            
            # Scale features
            scaled_features = np.zeros_like(symbol_features)
            for i, col in enumerate(feature_columns):
                scaler_key = f"{symbol}_{col}"
                if scaler_key not in self.feature_scalers:
                    self.feature_scalers[scaler_key] = MinMaxScaler()
                    scaled_features[:, i] = self.feature_scalers[scaler_key].fit_transform(
                        symbol_features[:, i].reshape(-1, 1)
                    ).flatten()
                else:
                    scaled_features[:, i] = self.feature_scalers[scaler_key].transform(
                        symbol_features[:, i].reshape(-1, 1)
                    ).flatten()
            
            # Create sequences
            for i in range(len(scaled_features) - self.sequence_length - self.forecast_horizon + 1):
                X.append(scaled_features[i:i + self.sequence_length])
                y.append(scaled_features[i + self.sequence_length, 0])  # Predict close price
                symbols.append(symbol)
        
        return np.array(X), np.array(y), symbols
    
    def inverse_transform_predictions(self, predictions, symbol):
        """Convert normalized predictions back to actual prices"""
        scaler_key = f"{symbol}_close"
        if scaler_key in self.feature_scalers:
            return self.feature_scalers[scaler_key].inverse_transform(
                predictions.reshape(-1, 1)
            ).flatten()
        return predictions


if __name__ == "__main__":
    print("\n🧪 TESTING DATA PREPROCESSOR\n")
    
    # Test with sample data
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    sample_data = pd.DataFrame({
        'date': dates.astype(str),
        'symbol': ['BTC'] * 100,
        'open': np.random.uniform(40000, 50000, 100),
        'high': np.random.uniform(45000, 55000, 100),
        'low': np.random.uniform(35000, 45000, 100),
        'close': np.random.uniform(40000, 50000, 100),
        'volume': np.random.uniform(1e9, 5e9, 100)
    })
    
    preprocessor = LSTMDataPreprocessor(sequence_length=14)
    X_train, X_test, y_train, y_test = preprocessor.prepare_data(sample_data)
    
    print(f"\n✅ Preprocessing test complete!")
    print(f"   X_train shape: {X_train.shape}")
    print(f"   y_train shape: {y_train.shape}")
