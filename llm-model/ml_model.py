"""
Real Machine Learning Model - Random Forest & Gradient Boosting for Crypto Prediction
Alternative to LSTM for Python 3.14 compatibility
Uses scikit-learn for REAL machine learning training
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import json
from datetime import datetime

class CryptoMLModel:
    """
    Real Machine Learning Model using Random Forest and Gradient Boosting
    
    Why These Models?
    - Random Forest: Ensemble of decision trees, handles non-linear patterns
    - Gradient Boosting: Sequential tree building, excellent for time series
    - Both are REAL ML algorithms with actual training/learning
    - Industry-standard for financial predictions
    - Faster than LSTM but still highly effective
    """
    
    def __init__(self, model_type='random_forest'):
        """
        Initialize ML model
        
        Args:
            model_type: 'random_forest' or 'gradient_boosting'
        """
        self.model_type = model_type
        self.model = None
        self.history = {
            'train_scores': [],
            'test_scores': [],
            'feature_importance': None
        }
        self.build_model()
        
    def build_model(self):
        """Build ML model"""
        print("\n" + "="*70)
        print("🏗️  BUILDING REAL MACHINE LEARNING MODEL")
        print("="*70 + "\n")
        
        if self.model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=200,          # 200 decision trees
                max_depth=15,              # Tree depth
                min_samples_split=5,       # Minimum samples to split
                min_samples_leaf=2,        # Minimum samples in leaf
                max_features='sqrt',       # Features per tree
                random_state=42,
                n_jobs=-1,                 # Use all CPU cores
                verbose=1                  # Show progress
            )
            model_name = "Random Forest"
            params = "200 trees, depth 15"
            
        else:  # gradient_boosting
            self.model = GradientBoostingRegressor(
                n_estimators=200,          # 200 boosting stages
                learning_rate=0.1,         # Shrinkage rate
                max_depth=5,               # Tree depth
                min_samples_split=5,
                min_samples_leaf=2,
                subsample=0.8,             # Stochastic gradient boosting
                random_state=42,
                verbose=1
            )
            model_name = "Gradient Boosting"
            params = "200 estimators, lr=0.1"
        
        print(f"✅ Model: {model_name}")
        print(f"   Parameters: {params}")
        print(f"   Algorithm: Real ensemble learning with decision trees")
        print("="*70)
        
    def train(self, X_train, y_train, X_test, y_test):
        """
        Train the ML model with REAL learning
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_test: Test features
            y_test: Test targets
            
        Returns:
            training results
        """
        print("\n" + "="*70)
        print("🚀 STARTING REAL MACHINE LEARNING TRAINING")
        print("="*70 + "\n")
        
        print(f"📊 Training Configuration:")
        print(f"   Model: {self.model_type.replace('_', ' ').title()}")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Test samples: {len(X_test)}")
        print(f"   Features: {X_train.shape[1]}")
        print(f"   Algorithm: Ensemble Learning (Real ML!)")
        print("\n" + "="*70 + "\n")
        
        # Train model (THIS IS REAL TRAINING!)
        print("🔥 Training in progress... (This is REAL machine learning!)\n")
        
        self.model.fit(X_train, y_train)
        
        print("\n" + "="*70)
        print("✅ TRAINING COMPLETE!")
        print("="*70)
        
        # Evaluate on train and test
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_score = r2_score(y_train, train_pred)
        test_score = r2_score(y_test, test_pred)
        
        self.history['train_scores'].append(train_score)
        self.history['test_scores'].append(test_score)
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            self.history['feature_importance'] = self.model.feature_importances_
        
        return {
            'train_score': train_score,
            'test_score': test_score,
            'train_pred': train_pred,
            'test_pred': test_pred
        }
    
    def evaluate(self, X_test, y_test):
        """Evaluate model on test set"""
        print("\n📊 Evaluating model on test set...")
        
        predictions = self.model.predict(X_test)
        
        mse = mean_squared_error(y_test, predictions)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        # MAPE
        mape = np.mean(np.abs((y_test - predictions) / (y_test + 1e-10))) * 100
        
        # Directional accuracy
        if len(y_test) > 1:
            actual_direction = np.diff(y_test) > 0
            pred_direction = np.diff(predictions) > 0
            directional_accuracy = np.mean(actual_direction == pred_direction) * 100
        else:
            directional_accuracy = 0
        
        metrics = {
            'mse': mse,
            'rmse': np.sqrt(mse),
            'mae': mae,
            'mape': mape,
            'r2': r2,
            'directional_accuracy': directional_accuracy
        }
        
        print(f"\n✅ Test Results:")
        print(f"   RMSE: {metrics['rmse']:.6f}")
        print(f"   MAE: {metrics['mae']:.6f}")
        print(f"   MAPE: {metrics['mape']:.2f}%")
        print(f"   R² Score: {metrics['r2']:.4f}")
        print(f"   Directional Accuracy: {metrics['directional_accuracy']:.2f}%")
        
        return metrics, predictions
    
    def cross_validate(self, X, y, cv=5):
        """Perform cross-validation"""
        print(f"\n📊 Performing {cv}-fold cross-validation...")
        
        scores = cross_val_score(self.model, X, y, cv=cv, 
                                scoring='r2', n_jobs=-1)
        
        print(f"   Cross-validation R² scores: {scores}")
        print(f"   Mean R² score: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
        
        return scores
    
    def predict(self, X):
        """Make predictions"""
        return self.model.predict(X)
    
    def save_model(self, filepath=None):
        """Save trained model"""
        if filepath is None:
            filepath = f"models/ml_model_{self.model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        joblib.dump(self.model, filepath)
        print(f"\n💾 Model saved to: {filepath}")
        
        # Save history
        history_file = filepath.replace('.pkl', '_history.json')
        with open(history_file, 'w') as f:
            json.dump({
                'train_scores': self.history['train_scores'],
                'test_scores': self.history['test_scores'],
                'model_type': self.model_type
            }, f, indent=2)
        print(f"💾 Training history saved to: {history_file}")
        
        return filepath
    
    @staticmethod
    def load_model(filepath):
        """Load a trained model"""
        model = joblib.load(filepath)
        print(f"✅ Model loaded from: {filepath}")
        return model
    
    def get_feature_importance(self, feature_names):
        """Get feature importance scores"""
        if self.history['feature_importance'] is not None:
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': self.history['feature_importance']
            }).sort_values('importance', ascending=False)
            return importance_df
        return None
    
    def get_model_summary(self):
        """Get model summary"""
        if self.model_type == 'random_forest':
            n_estimators = self.model.n_estimators
            max_depth = self.model.max_depth
        else:
            n_estimators = self.model.n_estimators
            max_depth = self.model.max_depth
        
        return {
            'model_type': self.model_type.replace('_', ' ').title(),
            'algorithm': 'Ensemble Learning',
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            'is_real_ml': True,
            'training_method': 'Supervised Learning with Decision Trees'
        }


if __name__ == "__main__":
    print("\n🧪 TESTING MACHINE LEARNING MODEL\n")
    
    # Create model
    model = CryptoMLModel(model_type='random_forest')
    
    # Test with random data
    X_train = np.random.random((1000, 9))
    y_train = np.random.random(1000)
    X_test = np.random.random((200, 9))
    y_test = np.random.random(200)
    
    # Train
    print("\n🔥 Running training test...")
    results = model.train(X_train, y_train, X_test, y_test)
    
    # Evaluate
    metrics, predictions = model.evaluate(X_test, y_test)
    
    print(f"\n✅ Model training successful!")
    print(f"   Train R²: {results['train_score']:.4f}")
    print(f"   Test R²: {results['test_score']:.4f}")
