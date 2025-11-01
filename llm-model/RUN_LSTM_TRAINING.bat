@echo off
chcp 65001 > nul
echo.
echo ================================================================================
echo    🚀 REAL MACHINE LEARNING TRAINING
echo ================================================================================
echo.
echo    This will train a REAL ML model on your crypto data!
echo.
echo    What this does:
echo    ✅ Generates 60 days of historical data from your 150+ snapshots
echo    ✅ Engineers features (RSI, Moving Averages, Volatility)
echo    ✅ Trains Random Forest with REAL ensemble learning
echo    ✅ Evaluates with proper metrics (RMSE, MAE, R², Directional Accuracy)
echo    ✅ Saves trained model and creates visualizations
echo.
echo    ⏱️  Estimated time: 2-5 minutes
echo.
echo    Note: Using Random Forest instead of LSTM due to Python 3.14 compatibility
echo          (TensorFlow doesn't support Python 3.14 yet)
echo.
echo ================================================================================
echo.

pause

echo.
echo 🔥 Starting ML training...
echo.

python train_lstm.py

echo.
echo ================================================================================
echo.
if %ERRORLEVEL% EQU 0 (
    echo ✅ ML TRAINING COMPLETE!
    echo.
    echo 📂 Check these folders:
    echo    - models/     : Trained ML model files (.joblib)
    echo    - plots/      : Training visualizations
    echo    - data/       : Historical data CSV
    echo.
    echo 💡 Your REAL machine learning model is ready for demonstration!
) else (
    echo ❌ Training failed! Check the error messages above.
    echo.
    echo 💡 Common fixes:
    echo    1. Install dependencies: pip install -r requirements_lstm.txt
    echo    2. Make sure you have training data in database
    echo    3. Check Python version (3.8+ required)
)
echo.
echo ================================================================================
echo.

pause
