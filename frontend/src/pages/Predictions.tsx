import React from 'react';

/**
 * Predictions Page Component
 * Shows AI-powered price predictions using LSTM, ARIMA, and Transformer models
 */
const Predictions: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold gradient-text">AI Price Predictions</h1>
      
      {/* Model Selection */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Prediction Models</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-700 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-400 mb-2">LSTM Model</h3>
            <p className="text-sm text-slate-300">Deep learning for time series forecasting</p>
            <div className="mt-2">
              <span className="text-xs bg-blue-600 px-2 py-1 rounded">Accuracy: 87.3%</span>
            </div>
          </div>
          
          <div className="bg-slate-700 p-4 rounded-lg">
            <h3 className="font-semibold text-green-400 mb-2">ARIMA Model</h3>
            <p className="text-sm text-slate-300">Statistical forecasting method</p>
            <div className="mt-2">
              <span className="text-xs bg-green-600 px-2 py-1 rounded">Accuracy: 82.1%</span>
            </div>
          </div>
          
          <div className="bg-slate-700 p-4 rounded-lg">
            <h3 className="font-semibold text-purple-400 mb-2">Transformer</h3>
            <p className="text-sm text-slate-300">Advanced attention-based model</p>
            <div className="mt-2">
              <span className="text-xs bg-purple-600 px-2 py-1 rounded">Accuracy: 89.7%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Current Predictions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Bitcoin Predictions</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span>24h Prediction</span>
              <span className="text-green-400 font-semibold">$46,250 (+2.8%)</span>
            </div>
            <div className="flex justify-between items-center">
              <span>7d Prediction</span>
              <span className="text-green-400 font-semibold">$48,100 (+6.9%)</span>
            </div>
            <div className="flex justify-between items-center">
              <span>30d Prediction</span>
              <span className="text-blue-400 font-semibold">$52,000 (+15.6%)</span>
            </div>
            <div className="mt-4 p-3 bg-slate-700 rounded-lg">
              <p className="text-sm text-slate-300">
                <strong>AI Insight:</strong> Strong bullish momentum detected with high confidence.
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Ethereum Predictions</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span>24h Prediction</span>
              <span className="text-green-400 font-semibold">$2,680 (+1.5%)</span>
            </div>
            <div className="flex justify-between items-center">
              <span>7d Prediction</span>
              <span className="text-green-400 font-semibold">$2,850 (+7.9%)</span>
            </div>
            <div className="flex justify-between items-center">
              <span>30d Prediction</span>
              <span className="text-green-400 font-semibold">$3,200 (+21.2%)</span>
            </div>
            <div className="mt-4 p-3 bg-slate-700 rounded-lg">
              <p className="text-sm text-slate-300">
                <strong>AI Insight:</strong> Upcoming upgrade driving positive sentiment.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Prediction Charts */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Prediction Visualization</h2>
        <div className="h-96 bg-slate-700 rounded-lg flex items-center justify-center">
          <p className="text-slate-400">AI Prediction Charts Will Be Here</p>
        </div>
      </div>

      {/* Model Confidence */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Model Confidence Scores</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-400 mb-2">87%</div>
            <p className="text-slate-300">LSTM Confidence</p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-400 mb-2">82%</div>
            <p className="text-slate-300">ARIMA Confidence</p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-400 mb-2">90%</div>
            <p className="text-slate-300">Transformer Confidence</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Predictions;
