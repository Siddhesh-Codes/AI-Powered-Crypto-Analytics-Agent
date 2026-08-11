import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.diagnostic import acorr_ljungbox
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
import logging
from typing import Tuple, Optional, Dict
import itertools

warnings.filterwarnings("ignore")

class ARIMAPricePredictor:
    """
    ARIMA (AutoRegressive Integrated Moving Average) Model for Cryptocurrency Price Prediction
    
    This class implements ARIMA modeling for time series forecasting of cryptocurrency prices.
    It includes automatic parameter selection, stationarity testing, and model validation.
    """
    
    def __init__(self, 
                 max_p: int = 5,
                 max_d: int = 2,
                 max_q: int = 5,
                 seasonal: bool = False,
                 information_criterion: str = 'aic'):
        """
        Initialize ARIMA Price Predictor
        
        Args:
            max_p: Maximum order of autoregression (AR)
            max_d: Maximum degree of differencing (I)
            max_q: Maximum order of moving average (MA)
            seasonal: Whether to use seasonal ARIMA
            information_criterion: Information criterion for model selection ('aic', 'bic')
        """
        self.max_p = max_p
        self.max_d = max_d
        self.max_q = max_q
        self.seasonal = seasonal
        self.information_criterion = information_criterion
        
        self.model = None
        self.fitted_model = None
        self.best_params = None
        self.is_trained = False
        self.original_data = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def check_stationarity(self, data: pd.Series, 
                          significance_level: float = 0.05) -> Dict:
        """
        Check if time series is stationary using Augmented Dickey-Fuller test
        
        Args:
            data: Time series data
            significance_level: Significance level for the test
            
        Returns:
            Dictionary containing stationarity test results
        """
        result = adfuller(data.dropna())
        
        is_stationary = result[1] <= significance_level
        
        stationarity_result = {
            'adf_statistic': result[0],
            'p_value': result[1],
            'critical_values': result[4],
            'is_stationary': is_stationary,
            'interpretation': 'Stationary' if is_stationary else 'Non-stationary'
        }
        
        self.logger.info(f"Stationarity Test - ADF Statistic: {result[0]:.4f}, "
                        f"p-value: {result[1]:.4f}, Is Stationary: {is_stationary}")
        
        return stationarity_result
    
    def make_stationary(self, data: pd.Series, max_diff: int = 2) -> Tuple[pd.Series, int]:
        """
        Make time series stationary through differencing
        
        Args:
            data: Time series data
            max_diff: Maximum number of differencing operations
            
        Returns:
            Tuple of (stationary_data, number_of_differences)
        """
        current_data = data.copy()
        diff_count = 0
        
        for d in range(max_diff + 1):
            stationarity = self.check_stationarity(current_data)
            
            if stationarity['is_stationary']:
                self.logger.info(f"Data became stationary after {d} differences")
                return current_data, d
            
            if d < max_diff:
                current_data = current_data.diff().dropna()
                diff_count += 1
        
        self.logger.warning(f"Data not stationary after {max_diff} differences")
        return current_data, diff_count
    
    def auto_arima(self, data: pd.Series) -> Tuple[int, int, int]:
        """
        Automatic ARIMA parameter selection using grid search
        
        Args:
            data: Time series data
            
        Returns:
            Best (p, d, q) parameters
        """
        self.logger.info("Starting automatic ARIMA parameter selection...")
        
        # Make data stationary and determine d
        stationary_data, d = self.make_stationary(data, self.max_d)
        
        best_aic = float('inf')
        best_bic = float('inf')
        best_params = None
        
        # Grid search for p and q
        for p in range(self.max_p + 1):
            for q in range(self.max_q + 1):
                try:
                    # Fit ARIMA model
                    model = ARIMA(data, order=(p, d, q))
                    fitted_model = model.fit()
                    
                    # Select based on information criterion
                    if self.information_criterion == 'aic':
                        criterion_value = fitted_model.aic
                        if criterion_value < best_aic:
                            best_aic = criterion_value
                            best_params = (p, d, q)
                    else:  # BIC
                        criterion_value = fitted_model.bic
                        if criterion_value < best_bic:
                            best_bic = criterion_value
                            best_params = (p, d, q)
                            
                except Exception as e:
                    continue
        
        if best_params is None:
            best_params = (1, d, 1)  # Default fallback
            self.logger.warning("Could not find optimal parameters, using default (1,d,1)")
        else:
            criterion_name = self.information_criterion.upper()
            best_value = best_aic if self.information_criterion == 'aic' else best_bic
            self.logger.info(f"Best ARIMA parameters: {best_params} with {criterion_name}: {best_value:.4f}")
        
        return best_params
    
    def train(self, price_data: pd.DataFrame, 
              price_column: str = 'close',
              validation_split: float = 0.2) -> Dict:
        """
        Train the ARIMA model
        
        Args:
            price_data: DataFrame containing price data
            price_column: Column name for price data
            validation_split: Fraction of data to use for validation
            
        Returns:
            Training metrics and model information
        """
        try:
            self.logger.info("Starting ARIMA model training...")
            
            # Prepare data
            self.original_data = price_data[price_column].copy()
            
            # Split data
            split_idx = int(len(self.original_data) * (1 - validation_split))
            train_data = self.original_data[:split_idx]
            val_data = self.original_data[split_idx:]
            
            # Find best parameters
            self.best_params = self.auto_arima(train_data)
            
            # Fit final model
            self.model = ARIMA(train_data, order=self.best_params)
            self.fitted_model = self.model.fit()
            
            # Generate predictions for validation
            forecast_steps = len(val_data)
            forecast = self.fitted_model.forecast(steps=forecast_steps)
            
            # Calculate metrics
            train_pred = self.fitted_model.fittedvalues
            
            # Align train predictions with actual values
            train_actual = train_data[len(train_data) - len(train_pred):]
            
            train_rmse = np.sqrt(mean_squared_error(train_actual, train_pred))
            val_rmse = np.sqrt(mean_squared_error(val_data, forecast))
            
            train_mae = mean_absolute_error(train_actual, train_pred)
            val_mae = mean_absolute_error(val_data, forecast)
            
            # Model diagnostics
            residuals = self.fitted_model.resid
            ljung_box_result = acorr_ljungbox(residuals, lags=10, return_df=True)
            
            self.is_trained = True
            
            metrics = {
                'best_params': self.best_params,
                'train_rmse': float(train_rmse),
                'val_rmse': float(val_rmse),
                'train_mae': float(train_mae),
                'val_mae': float(val_mae),
                'aic': float(self.fitted_model.aic),
                'bic': float(self.fitted_model.bic),
                'log_likelihood': float(self.fitted_model.llf),
                'ljung_box_p_value': float(ljung_box_result['lb_pvalue'].iloc[-1])
            }
            
            self.logger.info(f"Training completed. Validation RMSE: {val_rmse:.4f}")
            self.logger.info(f"Model parameters (p,d,q): {self.best_params}")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error during training: {str(e)}")
            raise
    
    def predict(self, steps_ahead: int = 1) -> np.ndarray:
        """
        Make price predictions
        
        Args:
            steps_ahead: Number of steps to predict ahead
            
        Returns:
            Predicted prices with confidence intervals
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            # Make forecast
            forecast_result = self.fitted_model.get_forecast(steps=steps_ahead)
            predictions = forecast_result.predicted_mean.values
            conf_int = forecast_result.conf_int().values
            
            return {
                'predictions': predictions,
                'lower_ci': conf_int[:, 0],
                'upper_ci': conf_int[:, 1]
            }
            
        except Exception as e:
            self.logger.error(f"Error during prediction: {str(e)}")
            raise
    
    def update_model(self, new_data: float):
        """
        Update model with new data point (for real-time predictions)
        
        Args:
            new_data: New price data point
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before updating")
        
        # Append new data and refit
        updated_data = pd.concat([self.original_data, pd.Series([new_data])])
        self.model = ARIMA(updated_data, order=self.best_params)
        self.fitted_model = self.model.fit()
        self.original_data = updated_data
    
    def get_model_summary(self) -> str:
        """Get model summary and diagnostics"""
        if not self.is_trained:
            return "Model not trained yet"
        
        return str(self.fitted_model.summary())
    
    def plot_diagnostics(self):
        """Plot model diagnostics"""
        if not self.is_trained:
            raise ValueError("Model must be trained before plotting diagnostics")
        
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Residuals plot
        residuals = self.fitted_model.resid
        axes[0, 0].plot(residuals)
        axes[0, 0].set_title('Residuals')
        axes[0, 0].set_xlabel('Time')
        axes[0, 0].set_ylabel('Residuals')
        
        # Q-Q plot
        from scipy import stats
        stats.probplot(residuals, dist="norm", plot=axes[0, 1])
        axes[0, 1].set_title('Q-Q Plot')
        
        # Histogram of residuals
        axes[1, 0].hist(residuals, bins=30, density=True, alpha=0.7)
        axes[1, 0].set_title('Histogram of Residuals')
        axes[1, 0].set_xlabel('Residuals')
        axes[1, 0].set_ylabel('Frequency')
        
        # ACF of residuals
        from statsmodels.graphics.tsaplots import plot_acf
        plot_acf(residuals, ax=axes[1, 1], lags=20)
        axes[1, 1].set_title('ACF of Residuals')
        
        plt.tight_layout()
        plt.show()


# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    
    # Generate synthetic price data with trend and some seasonality
    trend = np.linspace(100, 200, len(dates))
    seasonal = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
    noise = np.random.randn(len(dates)) * 5
    prices = trend + seasonal + noise
    
    sample_data = pd.DataFrame({
        'date': dates,
        'close': prices
    })
    
    # Test ARIMA predictor
    predictor = ARIMAPricePredictor(max_p=3, max_q=3, max_d=2)
    
    # Train model
    metrics = predictor.train(sample_data)
    print("Training Metrics:", metrics)
    
    # Make predictions
    predictions = predictor.predict(steps_ahead=7)
    print("7-day predictions:", predictions)
