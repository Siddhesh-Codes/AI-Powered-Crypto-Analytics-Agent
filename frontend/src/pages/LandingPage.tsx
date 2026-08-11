import React, { useEffect, useState, useRef } from 'react';
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
  const [visibleElements, setVisibleElements] = useState<Set<string>>(new Set());
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setVisibleElements((prev) => new Set([...prev, entry.target.id]));
          }
        });
      },
      {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
      }
    );

    // Small delay to ensure DOM is fully rendered
    const timer = setTimeout(() => {
      const elements = document.querySelectorAll('[data-animate]');
      elements.forEach((el) => observerRef.current?.observe(el));
    }, 100);

    return () => {
      clearTimeout(timer);
      observerRef.current?.disconnect();
    };
  }, []);
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



  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(50px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes slideInLeft {
          from {
            opacity: 0;
            transform: translateX(-50px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(50px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        @keyframes scaleIn {
          from {
            opacity: 0;
            transform: scale(0.9);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        

        
        [data-animate] {
          opacity: 0;
          transition: all 0.6s ease-out;
        }
        
        [data-animate].animate-fadeInUp {
          animation: fadeInUp 0.8s ease-out forwards;
        }
        
        [data-animate].animate-slideInLeft {
          animation: slideInLeft 0.8s ease-out forwards;
        }
        
        [data-animate].animate-slideInRight {
          animation: slideInRight 0.8s ease-out forwards;
        }
        
        [data-animate].animate-scaleIn {
          animation: scaleIn 0.8s ease-out forwards;
        }
        

        
        .delay-100 { animation-delay: 0.1s; }
        .delay-200 { animation-delay: 0.2s; }
        .delay-300 { animation-delay: 0.3s; }
        .delay-400 { animation-delay: 0.4s; }
        .delay-500 { animation-delay: 0.5s; }
      `}</style>
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
                to="/login" 
                className="text-slate-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Sign In
              </Link>
              <Link 
                to="/register" 
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
            <h1 
              id="hero-title" 
              data-animate 
              className={`text-4xl md:text-6xl font-bold text-white mb-6 ${visibleElements.has('hero-title') ? 'animate-fadeInUp' : ''}`}
            >
              AI-Powered Crypto
              <span className="bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent block">
                Analytics & Forecasting
              </span>
            </h1>
            <p 
              id="hero-desc" 
              data-animate 
              className={`text-xl text-slate-300 mb-8 max-w-3xl mx-auto delay-200 ${visibleElements.has('hero-desc') ? 'animate-fadeInUp' : ''}`}
            >
              Make smarter investment decisions with our advanced AI models. Get real-time insights, 
              machine learning predictions, and comprehensive portfolio analysis all in one platform.
            </p>
            <div 
              id="hero-buttons" 
              data-animate 
              className={`flex flex-col sm:flex-row gap-4 justify-center delay-400 ${visibleElements.has('hero-buttons') ? 'animate-fadeInUp' : ''}`}
            >
              <Link 
                to="/auth?force=true" 
                className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105"
              >
                Get Started
                <ArrowRight className="ml-2 w-4 h-4" />
              </Link>
              <button className="inline-flex items-center px-8 py-3 border border-slate-600 text-base font-medium rounded-lg text-slate-300 hover:text-white hover:border-slate-500 transition-all duration-200 hover:scale-105">
                Learn More
              </button>
            </div>
          </div>
        </div>
      </section>



      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 
              id="features-title" 
              data-animate 
              className={`text-3xl md:text-4xl font-bold text-white mb-4 ${visibleElements.has('features-title') ? 'animate-fadeInUp' : ''}`}
            >
              Powerful Features for Smart Trading
            </h2>
            <p 
              id="features-desc" 
              data-animate 
              className={`text-xl text-slate-300 max-w-2xl mx-auto delay-200 ${visibleElements.has('features-desc') ? 'animate-fadeInUp' : ''}`}
            >
              Everything you need to analyze, predict, and optimize your cryptocurrency investments
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div 
                key={index} 
                id={`feature-${index}`}
                data-animate
                className={`bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700 hover:border-slate-600 transition-all duration-300 hover:transform hover:scale-105 hover:shadow-xl hover:shadow-blue-500/20 delay-${(index + 1) * 100} ${visibleElements.has(`feature-${index}`) ? 'animate-scaleIn' : ''}`}
              >
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
            <h2 
              id="how-it-works-title" 
              data-animate 
              className={`text-3xl md:text-4xl font-bold text-white mb-4 ${visibleElements.has('how-it-works-title') ? 'animate-fadeInUp' : ''}`}
            >
              How It Works
            </h2>
            <p 
              id="how-it-works-desc" 
              data-animate 
              className={`text-xl text-slate-300 delay-200 ${visibleElements.has('how-it-works-desc') ? 'animate-fadeInUp' : ''}`}
            >
              Get started in just 3 simple steps
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div 
              id="step-1" 
              data-animate 
              className={`text-center delay-100 ${visibleElements.has('step-1') ? 'animate-slideInLeft' : ''}`}
            >
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
            
            <div 
              id="step-2" 
              data-animate 
              className={`text-center delay-300 ${visibleElements.has('step-2') ? 'animate-fadeInUp' : ''}`}
            >
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
            
            <div 
              id="step-3" 
              data-animate 
              className={`text-center delay-500 ${visibleElements.has('step-3') ? 'animate-slideInRight' : ''}`}
            >
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
          <div 
            id="cta-section" 
            data-animate 
            className={`bg-gradient-to-r from-blue-500/10 to-purple-600/10 rounded-2xl p-8 border border-slate-700 transition-all duration-300 hover:border-blue-500/50 hover:shadow-xl hover:shadow-blue-500/20 ${visibleElements.has('cta-section') ? 'animate-scaleIn' : ''}`}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to Transform Your Crypto Trading?
            </h2>
            <p className="text-xl text-slate-300 mb-8">
              Experience the power of AI-driven cryptocurrency analytics and make informed investment decisions
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                to="/auth?force=true" 
                className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105"
              >
                Get Started
                <ArrowRight className="ml-2 w-4 h-4" />
              </Link>
            </div>
            <div className="mt-6 flex items-center justify-center space-x-6 text-sm text-slate-400">
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 mr-1" />
                Real-time market data
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 mr-1" />
                AI-powered analytics
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 mr-1" />
                Portfolio management
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
