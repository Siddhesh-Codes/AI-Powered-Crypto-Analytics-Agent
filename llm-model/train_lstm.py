"""
Real ML Training Pipeline - Complete training workflow with real machine learning
Uses Random Forest / Gradient Boosting (compatible with Python 3.14)
Integrates data generation, preprocessing, model training, and evaluation
"""

import numpy as np
import pandas as pd
import time
from datetime import datetime
from historical_generator import HistoricalDataGenerator
from data_preprocessor import LSTMDataPreprocessor
from ml_model import CryptoMLModel  # Using scikit-learn instead of TensorFlow
from database_manager import TrainingDataDB
import matplotlib.pyplot as plt
import seaborn as sns

class MLTrainingPipeline:
    """Complete Real ML training pipeline"""
    
    def __init__(self):
        self.db = TrainingDataDB()
        self.generator = HistoricalDataGenerator(lookback_days=60)
        self.preprocessor = LSTMDataPreprocessor(sequence_length=14)
        self.model = None
        self.session_id = None
        self.start_time = None
        self.feature_names = ['close', 'volume', 'price_change', 'price_range', 
                             'ma_7', 'ma_14', 'volatility', 'rsi', 'volume_change']
        
    def run_complete_pipeline(self, model_type='random_forest'):
        """Execute complete training pipeline"""
        print("\n" + "="*80)
        print("🤖 REAL MACHINE LEARNING TRAINING PIPELINE")
        print("="*80)
        print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Model: {model_type.replace('_', ' ').title()}")
        print("="*80 + "\n")
        
        self.start_time = time.time()
        
        # Step 1: Generate historical data
        print("📊 STEP 1: GENERATING HISTORICAL DATA")
        print("-" * 80)
        historical_data = self.generator.generate_historical_sequences()
        
        if historical_data is None or len(historical_data) == 0:
            print("❌ Failed to generate historical data!")
            return
        
        print(f"✅ Generated {len(historical_data)} historical data points")
        time.sleep(1)
        
        # Step 2: Preprocess data
        print("\n📊 STEP 2: PREPROCESSING DATA")
        print("-" * 80)
        X_train, X_test, y_train, y_test = self.preprocessor.prepare_data(historical_data)
        
        print(f"✅ Data preprocessing complete")
        print(f"   Training sequences: {len(X_train)}")
        print(f"   Testing sequences: {len(X_test)}")
        time.sleep(1)
        
        # Step 3: Build ML model
        print("\n📊 STEP 3: BUILDING MACHINE LEARNING MODEL")
        print("-" * 80)
        
        # Flatten sequences for traditional ML (Random Forest doesn't need sequences)
        X_train_flat = X_train.reshape(X_train.shape[0], -1)
        X_test_flat = X_test.reshape(X_test.shape[0], -1)
        
        self.model = CryptoMLModel(model_type=model_type)
        
        # Create training session in database
        session_data = {
            'session_name': f"ML_Training_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'model_name': model_type.replace('_', ' ').title(),
            'num_epochs': 1,  # ML models don't use epochs
            'batch_size': 0,  # Not applicable for ML
            'learning_rate': 0.1,
            'total_crypto_records': len(historical_data),
            'total_news_records': 0
        }
        self.session_id = self.db.create_training_session(session_data)
        print(f"✅ Training session created (ID: {self.session_id})")
        time.sleep(1)
        
        # Step 4: Train model (REAL MACHINE LEARNING!)
        print("\n📊 STEP 4: TRAINING ML MODEL")
        print("-" * 80)
        
        training_results = self.model.train(
            X_train_flat, y_train,
            X_test_flat, y_test
        )
        
        # Step 5: Evaluate model
        print("\n📊 STEP 5: MODEL EVALUATION")
        print("-" * 80)
        test_metrics, y_pred = self.model.evaluate(X_test_flat, y_test)
        
        # Cross-validation
        print("\n� Performing Cross-Validation...")
        cv_scores = self.model.cross_validate(X_train_flat, y_train, cv=5)
        
        print(f"\n📊 FINAL METRICS:")
        print(f"   RMSE: {test_metrics['rmse']:.6f}")
        print(f"   MAE: {test_metrics['mae']:.6f}")
        print(f"   MAPE: {test_metrics['mape']:.2f}%")
        print(f"   R² Score: {test_metrics['r2']:.4f}")
        print(f"   Directional Accuracy: {test_metrics['directional_accuracy']:.2f}%")
        print(f"   Cross-Validation R²: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Step 6: Save model
        print("\n📊 STEP 6: SAVING MODEL")
        print("-" * 80)
        model_path = self.model.save_model()
        
        # Save additional metadata for predictor service
        model_info_path = model_path.replace('.pkl', '.json')
        with open(model_info_path, 'w') as f:
            import json
            json.dump({
                'model_type': self.model.model_type,
                'training_date': datetime.now().isoformat(),
                'test_score': float(test_metrics['r2']),
                'num_features': X_train_flat.shape[1],
                'directional_accuracy': float(test_metrics['directional_accuracy']),
                'mae': float(test_metrics['mae']),
                'mape': float(test_metrics['mape']),
                'cv_score_mean': float(cv_scores.mean()),
                'cv_score_std': float(cv_scores.std())
            }, f, indent=2)
        print(f"💾 Model metadata saved to: {model_info_path}")
        
        # Step 7: Create visualizations
        print("\n📊 STEP 7: GENERATING VISUALIZATIONS")
        print("-" * 80)
        self._create_visualizations(training_results, y_test, y_pred, test_metrics)
        
        # Feature importance (skip for now as features are flattened)
        if self.model.history['feature_importance'] is not None:
            top_features_idx = np.argsort(self.model.history['feature_importance'])[-5:][::-1]
            print("\n📊 TOP 5 MOST IMPORTANT FEATURES:")
            for idx in top_features_idx:
                print(f"   Feature {idx}: {self.model.history['feature_importance'][idx]:.4f}")
        
        # Update database with results
        training_duration = time.time() - self.start_time
        results = {
            'final_train_loss': 1.0 - training_results['train_score'],  # Convert R² to loss
            'final_val_loss': 1.0 - training_results['test_score'],
            'final_accuracy': float(test_metrics['directional_accuracy']),
            'training_duration': training_duration
        }
        self.db.update_training_session(self.session_id, results)
        
        # Print summary
        print("\n" + "="*80)
        print("🎉 REAL MACHINE LEARNING TRAINING COMPLETE!")
        print("="*80)
        print(f"\n⏱️  Total Time: {training_duration:.2f} seconds ({training_duration/60:.1f} minutes)")
        print(f"\n📊 Final Results:")
        print(f"   Model: {self.model.model_type.replace('_', ' ').title()}")
        print(f"   Algorithm: Ensemble Learning (Real ML!)")
        print(f"   Training Samples: {len(X_train)}")
        print(f"   Test Samples: {len(X_test)}")
        print(f"   Training R²: {training_results['train_score']:.4f}")
        print(f"   Test R²: {training_results['test_score']:.4f}")
        print(f"   Directional Accuracy: {test_metrics['directional_accuracy']:.2f}%")
        print(f"   RMSE: {test_metrics['rmse']:.6f}")
        print(f"   Cross-Val R²: {cv_scores.mean():.4f}")
        print(f"\n💾 Model saved to: {model_path}")
        print(f"📊 Visualizations saved to: plots/")
        print(f"📚 Training history saved to database")
        
        print("\n" + "="*80)
        print("✅ YOUR REAL ML MODEL IS READY FOR DEMONSTRATION!")
        print("="*80 + "\n")
        
        self.db.close()
        
    def _create_visualizations(self, training_results, y_test, y_pred, metrics):
        """Create comprehensive visualizations"""
        
        # Set style
        try:
            import seaborn as sns
            sns.set_style("whitegrid")
        except:
            pass
        
        # 1. Training Results
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # R² scores
        scores = ['Train R²', 'Test R²']
        values = [training_results['train_score'], training_results['test_score']]
        axes[0, 0].bar(scores, values, color=['#2ecc71', '#3498db'])
        axes[0, 0].set_title('Model Performance (R² Score)', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylabel('R² Score')
        axes[0, 0].set_ylim([0, 1])
        axes[0, 0].grid(True, alpha=0.3)
        for i, v in enumerate(values):
            axes[0, 0].text(i, v + 0.02, f'{v:.4f}', ha='center', fontweight='bold')
        
        # Feature importance (if available)
        if self.model.history['feature_importance'] is not None:
            importance = self.model.history['feature_importance']
            sorted_idx = np.argsort(importance)[-9:]  # Top 9 features
            axes[0, 1].barh(range(len(sorted_idx)), importance[sorted_idx])
            axes[0, 1].set_yticks(range(len(sorted_idx)))
            # Feature names are repeated for each time step, so just show top importance
            feature_labels = [f'Feature {i}' for i in sorted_idx]
            axes[0, 1].set_yticklabels(feature_labels)
            axes[0, 1].set_title('Top Feature Importance', fontsize=14, fontweight='bold')
            axes[0, 1].set_xlabel('Importance Score')
            axes[0, 1].grid(True, alpha=0.3)
        else:
            axes[0, 1].text(0.5, 0.5, 'Feature Importance\nNot Available', 
                           ha='center', va='center', fontsize=12)
            axes[0, 1].set_title('Feature Importance', fontsize=14, fontweight='bold')
        
        # Predictions vs Actual
        axes[1, 0].scatter(y_test, y_pred, alpha=0.5, s=20)
        axes[1, 0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 
                       'r--', linewidth=2, label='Perfect Prediction')
        axes[1, 0].set_title('Predictions vs Actual Values', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Actual Values')
        axes[1, 0].set_ylabel('Predicted Values')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Prediction errors
        errors = y_test.flatten() - y_pred.flatten()
        axes[1, 1].hist(errors, bins=50, edgecolor='black', alpha=0.7)
        axes[1, 1].set_title('Prediction Error Distribution', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('Prediction Error')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].axvline(0, color='r', linestyle='--', linewidth=2)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'plots/ml_training_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Time series predictions
        fig, ax = plt.subplots(figsize=(15, 6))
        
        sample_size = min(100, len(y_test))
        x_axis = range(sample_size)
        
        ax.plot(x_axis, y_test[:sample_size], label='Actual', linewidth=2, marker='o', markersize=4)
        ax.plot(x_axis, y_pred[:sample_size], label='Predicted', linewidth=2, marker='s', markersize=4)
        ax.set_title('ML Price Predictions (Sample)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Sample Index')
        ax.set_ylabel('Normalized Price')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'plots/ml_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Visualizations created successfully!")


def main():
    """Main execution function"""
    pipeline = MLTrainingPipeline()
    
    # Run with configuration (Random Forest or Gradient Boosting)
    pipeline.run_complete_pipeline(
        model_type='random_forest'  # or 'gradient_boosting'
    )


if __name__ == "__main__":
    main()
