import React from 'react';
import { Link } from 'react-router-dom';
import { 
  TrendingUp, 
  Brain, 
  Shield, 
  Zap, 
  BarChart3, 
  MessageCircle,
  ArrowRight,
  CheckCircle
} from 'lucide-react';

/**
 * Landing Page Component
 * Professional homepage introducing the AI-Powered Crypto Analytics platform
 */
const LandingPage: React.FC = () => {
  const features = [
    {
      icon: <Brain className="w-6 h-6" />,
      title: "AI-Powered Predictions",
      description: "Advanced LSTM, ARIMA, and Transformer models for accurate price forecasting"
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Technical Analysis",
      description: "Real-time RSI, MACD, Bollinger Bands, and custom trading indicators"
    },
    {
      icon: <MessageCircle className="w-6 h-6" />,
      title: "24/7 AI Chatbot",
      description: "Get instant answers about crypto markets and your portfolio performance"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Risk Assessment",
      description: "Comprehensive portfolio risk analysis and protection strategies"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Real-time Data",
      description: "Live market data, price alerts, and instant trading signals"
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Portfolio Tracking",
      description: "Connect exchanges, track performance, and optimize your investments"
    }
  ];

  const stats = [
    { number: "99.2%", label: "Prediction Accuracy" },
    { number: "50K+", label: "Active Users" },
    { number: "15+", label: "Supported Exchanges" },
    { number: "24/7", label: "Market Monitoring" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-slate-900/80 backdrop-blur-lg border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                  CryptoAI
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                to="/auth" 
                className="text-slate-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Sign In
              </Link>
              <Link 
                to="/auth?force=true" 
                className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 transform hover:scale-105"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              AI-Powered Crypto
              <span className="bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent block">
                Analytics & Forecasting
              </span>
            </h1>
            <p className="text-xl text-slate-300 mb-8 max-w-3xl mx-auto">
              Make smarter investment decisions with our advanced AI models. Get real-time insights, 
              accurate predictions, and comprehensive portfolio analysis all in one platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                to="/auth?force=true" 
                className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105"
              >
                Start Free Trial
                <ArrowRight className="ml-2 w-4 h-4" />
              </Link>
              <button className="inline-flex items-center px-8 py-3 border border-slate-600 text-base font-medium rounded-lg text-slate-300 hover:text-white hover:border-slate-500 transition-colors">
                Watch Demo
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-white mb-2">
                  {stat.number}
                </div>
                <div className="text-slate-400 text-sm">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Powerful Features for Smart Trading
            </h2>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto">
              Everything you need to analyze, predict, and optimize your cryptocurrency investments
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700 hover:border-slate-600 transition-all duration-200 hover:transform hover:scale-105">
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 w-12 h-12 rounded-lg flex items-center justify-center text-white mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-slate-300">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              How It Works
            </h2>
            <p className="text-xl text-slate-300">
              Get started in just 3 simple steps
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 w-16 h-16 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-4 mx-auto">
                1
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Connect Your Portfolio
              </h3>
              <p className="text-slate-300">
                Link your exchange accounts or manually add your holdings to start tracking
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 w-16 h-16 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-4 mx-auto">
                2
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                AI Analysis
              </h3>
              <p className="text-slate-300">
                Our AI models analyze market data and generate personalized insights for your portfolio
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 w-16 h-16 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-4 mx-auto">
                3
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Make Informed Decisions
              </h3>
              <p className="text-slate-300">
                Get real-time predictions, risk assessments, and trading recommendations
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-r from-blue-500/10 to-purple-600/10 rounded-2xl p-8 border border-slate-700">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to Supercharge Your Crypto Trading?
            </h2>
            <p className="text-xl text-slate-300 mb-8">
              Join thousands of traders who are already using AI to maximize their returns
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                to="/auth?force=true" 
                className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105"
              >
                Start Your Free Trial
                <ArrowRight className="ml-2 w-4 h-4" />
              </Link>
            </div>
            <div className="mt-6 flex items-center justify-center space-x-6 text-sm text-slate-400">
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 mr-1" />
                No credit card required
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 mr-1" />
                14-day free trial
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 mr-1" />
                Cancel anytime
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-4">
              CryptoAI
            </h3>
            <p className="text-slate-400 mb-8">
              AI-Powered Crypto Analytics & Forecasting Platform
            </p>
            <div className="text-sm text-slate-500">
              © 2025 CryptoAI. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
