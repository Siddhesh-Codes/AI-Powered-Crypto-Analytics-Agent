import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, MessageCircle, X, Minimize2, Maximize2, HelpCircle, Calculator, TrendingUp, DollarSign, Target, Zap, Brain, Mic, MicOff, Copy, ThumbsUp, ThumbsDown, Settings, BarChart3, PieChart, AlertTriangle } from 'lucide-react';
import { useMarketStore } from '../../store/marketStore';
import { usePortfolioStore } from '../../store/portfolioStore';
import toast from 'react-hot-toast';
import './AIChatbot.css';

/**
 * AI Chat Message Interface
 */
export interface ChatMessage {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  suggestions?: string[];
  tools?: Array<{
    name: string;
    icon: string;
    action: string;
    data?: any;
  }>;
  charts?: Array<{
    type: 'price' | 'volume' | 'marketcap';
    symbol: string;
    data: number[];
  }>;
  alerts?: Array<{
    type: 'bullish' | 'bearish' | 'neutral' | 'warning';
    message: string;
  }>;
}

/**
 * Enhanced AI Chatbot Component with Real AI Backend
 */
interface AIChatbotProps {
  isOpen: boolean;
  onToggle: () => void;
  className?: string;
}

export const AIChatbot: React.FC<AIChatbotProps> = ({
  isOpen,
  onToggle,
  className = '',
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'bot',
      content: '🚀 **Welcome to REAL AI Crypto Assistant v2.0!** 🤖\n\n✨ **NO MORE PRE-DEFINED RESPONSES!**\n\n🧠 **Powered by Multiple AI Models:**\n• 🔥 OpenAI GPT-4 (Premium intelligence)\n• ⚡ Groq Mixtral-8x7B (Ultra-fast responses)\n• 🎯 Claude-3 (Advanced reasoning)\n\n💫 **What makes me special:**\n• 🤖 Real AI intelligence - each response is unique!\n• 📊 Live market data integration\n• 💡 Personalized analysis based on your portfolio\n• 🎭 Conversation awareness - I remember our chat!\n\n🎯 **Ask me ANYTHING about crypto!**\nTry: "Give me an overview of Bitcoin for the last 7 days" or "Analyze my portfolio performance"\n\n*Every response is generated fresh by real AI models!*',
      timestamp: new Date(),
      suggestions: [
        '📊 Bitcoin 7-day analysis',
        '💰 Review my portfolio performance',
        '🧮 Profit calculator',
        '📈 Best altcoins now',
        '⚡ Trading strategy advice'
      ],
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [chatTheme, setChatTheme] = useState<'dark' | 'light' | 'crypto'>('crypto');
  const [showTools, setShowTools] = useState(false);
  const [aiStatus, setAiStatus] = useState<'online' | 'offline'>('online');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const { topCryptos, globalMetrics, marketSentiment } = useMarketStore();
  const { assets, totalValue, totalChangePercent24h } = usePortfolioStore();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when chatbot opens
  useEffect(() => {
    if (isOpen && !isMinimized) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen, isMinimized]);

  // Check AI service health on mount
  useEffect(() => {
    checkAIHealth();
    // Check AI health every 10 seconds
    const interval = setInterval(checkAIHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkAIHealth = async () => {
    try {
      console.log('🔍 Checking AI backend health...');
      const response = await fetch('http://localhost:8000/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const healthData = await response.json();
        console.log('✅ Backend health check successful:', healthData);
        setAiStatus('online');
      } else {
        console.warn('⚠️ Backend health check failed:', response.status);
        setAiStatus('offline');
      }
    } catch (error) {
      console.error('❌ Backend health check error:', error);
      setAiStatus('offline');
    }
  };

  const generateRealAIResponse = async (userMessage: string): Promise<ChatMessage> => {
    try {
      console.log('🤖 Calling Real AI Backend for message:', userMessage);
      
      const requestBody = {
        message: userMessage,
        conversation_history: messages.slice(-5).map(msg => ({
          role: msg.type === 'user' ? 'user' : 'assistant',
          content: msg.content,
          timestamp: msg.timestamp
        })),
        user_context: {
          portfolio_value: totalValue,
          portfolio_change: totalChangePercent24h,
          assets_count: assets.length,
          top_cryptos: topCryptos.slice(0, 5),
          current_page: window.location.pathname,
          timestamp: new Date().toISOString()
        }
      };
      
      console.log('📤 Sending request to Real AI Backend...');
      
      const response = await fetch('http://localhost:8000/api/v1/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      console.log('📡 Response status:', response.status, response.statusText);

      if (response.ok) {
        const aiData = await response.json();
        console.log('✅ Real AI Response received from:', aiData.source);
        console.log('🤖 AI Response:', aiData.response.substring(0, 100) + '...');
        
        setAiStatus('online');
        
        return {
          id: Date.now().toString(),
          type: 'bot',
          content: `🤖 **Real AI Response** (Source: ${aiData.source})\n\n${aiData.response}`,
          timestamp: new Date(),
          suggestions: aiData.suggestions || [],
          tools: generateToolsFromResponse(aiData.response),
          alerts: generateAlertsFromResponse(aiData.response),
        };
      } else {
        const errorText = await response.text();
        console.error('❌ AI Backend Error:', response.status, errorText);
        throw new Error(`Backend error: ${response.status}`);
      }

      if (response.ok) {
        const aiData = await response.json();
        console.log('✅ Real AI Response received:', aiData);
        console.log('🎯 Response source:', aiData.source);
        console.log('📝 Response length:', aiData.response?.length || 0, 'characters');
        
        setAiStatus('online');
        
        return {
          id: Date.now().toString(),
          type: 'bot',
          content: aiData.response,
          timestamp: new Date(),
          suggestions: aiData.suggestions || [],
          tools: generateToolsFromResponse(aiData.response),
          alerts: generateAlertsFromResponse(aiData.response),
        };
      } else {
        const errorText = await response.text();
        console.error('❌ Backend response error:', response.status, errorText);
        throw new Error(`AI backend error: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('💥 AI backend connection failed:', error);
      setAiStatus('offline');
      
      return {
        id: Date.now().toString(),
        type: 'bot',
        content: `🚨 **Backend Connection Failed!**\n\n` +
          `❌ **Error**: Could not connect to AI backend\n\n` +
          `🔧 **Fix Steps:**\n` +
          `1. Make sure backend is running: \`python simple_backend.py\`\n` +
          `2. Check backend is at: http://localhost:8000\n` +
          `3. Verify API key is configured\n` +
          `4. Check console for backend errors\n\n` +
          `**I REFUSE to give pre-defined responses!**\n` +
          `Only real AI intelligence allowed! 🤖✨\n\n` +
          `Error details: ${error}`,
        timestamp: new Date(),
        suggestions: ['Start backend', 'Check API key', 'Restart app', 'Check logs'],
        tools: [],
        alerts: [],
      };
    }
  };

  const generateToolsFromResponse = (response: string): any[] => {
    const tools = [];
    
    if (response.includes('calculator') || response.includes('profit')) {
      tools.push({ name: 'Calculator', icon: 'calculator', action: 'calc' });
    }
    if (response.includes('technical') || response.includes('analysis')) {
      tools.push({ name: 'TA Tools', icon: 'trending-up', action: 'ta_tools' });
    }
    if (response.includes('alert') || response.includes('price')) {
      tools.push({ name: 'Price Alert', icon: 'target', action: 'set_alert' });
    }
    
    return tools;
  };

  const generateAlertsFromResponse = (response: string): any[] => {
    const alerts = [];
    
    if (response.includes('profits') && response.includes('strong')) {
      alerts.push({ type: 'bullish', message: 'Strong performance detected - consider profit taking' });
    }
    if (response.includes('accumulation') || response.includes('opportunity')) {
      alerts.push({ type: 'bullish', message: 'Potential buying opportunity identified' });
    }
    
    return alerts;
  };

  const handleSendMessage = async (messageText?: string) => {
    const text = messageText || inputMessage.trim();
    if (!text) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: text,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const botResponse = await generateRealAIResponse(text);
      setMessages(prev => [...prev, botResponse]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: '🚨 I\'m experiencing technical difficulties. Please try again in a moment.\n\n*Tip: Try simpler queries like "Bitcoin analysis" or "portfolio help"*',
        timestamp: new Date(),
        suggestions: ['Bitcoin analysis', 'Portfolio help', 'Market trends', 'Try again'],
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion);
  };

  const handleToolAction = (tool: any) => {
    switch (tool.action) {
      case 'calc':
        handleSendMessage('Show me profit calculator');
        break;
      case 'ta_tools':
        handleSendMessage('Technical analysis for Bitcoin');
        break;
      case 'set_alert':
        handleSendMessage('Set up price alerts');
        break;
      default:
        handleSendMessage(`Help me with ${tool.name.toLowerCase()}`);
    }
  };

  const toggleVoiceInput = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setIsListening(!isListening);
      setTimeout(() => setIsListening(false), 3000);
    } else {
      toast.error('Voice input not supported in your browser');
    }
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    toast.success('Message copied to clipboard!');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getThemeClasses = () => {
    switch (chatTheme) {
      case 'light':
        return {
          container: 'bg-white border-gray-300',
          header: 'bg-gradient-to-r from-blue-500 to-purple-500',
          message: 'bg-gray-100 text-gray-900 border-gray-200',
          input: 'bg-gray-50 border-gray-300 text-gray-900'
        };
      case 'crypto':
        return {
          container: 'bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900 border-purple-500/30',
          header: 'bg-gradient-to-r from-purple-600 via-blue-600 to-green-600',
          message: 'bg-slate-800/80 text-slate-100 border-purple-500/30',
          input: 'bg-slate-800/50 border-purple-500/50 text-white'
        };
      default:
        return {
          container: 'bg-slate-900 border-slate-700',
          header: 'bg-gradient-to-r from-blue-600 to-purple-600',
          message: 'bg-slate-800 text-slate-100 border-slate-700',
          input: 'bg-slate-800 border-slate-600 text-white'
        };
    }
  };

  const themeClasses = getThemeClasses();

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end space-y-3">
        <button
          onClick={onToggle}
          className={`group bg-gradient-to-r from-purple-600 via-blue-600 to-green-600 hover:from-purple-700 hover:via-blue-700 hover:to-green-700 text-white p-4 rounded-full shadow-2xl transition-all duration-300 hover:scale-110 animate-pulse ${className}`}
          title="Real AI Crypto Assistant"
        >
          <div className="relative">
            <Brain className="w-6 h-6" />
            <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full animate-ping ${
              aiStatus === 'online' ? 'bg-green-400' : 'bg-red-400'
            }`}></div>
          </div>
        </button>
        
        <div className="absolute -top-2 -left-2 bg-red-500 text-white text-xs px-2 py-1 rounded-full animate-bounce">
          REAL AI!
        </div>
      </div>
    );
  }

  return (
    <div className={`fixed bottom-6 right-6 z-50 ${className}`}>
      <div className={`${themeClasses.container} rounded-xl shadow-2xl transition-all duration-300 ${
        isMinimized ? 'w-80 h-16' : 'w-96 h-[700px]'
      } backdrop-blur-lg`}>
        
        {/* Enhanced Header */}
        <div className={`flex items-center justify-between p-4 border-b border-slate-700 ${themeClasses.header} rounded-t-xl relative overflow-hidden`}>
          <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 via-blue-600/20 to-green-600/20 animate-pulse"></div>
          <div className="flex items-center space-x-3 relative z-10">
            <div className="w-8 h-8 bg-white/90 rounded-full flex items-center justify-center animate-bounce">
              <Brain className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <h3 className="font-bold text-white">Real AI Crypto Assistant 🚀</h3>
              <p className="text-xs text-blue-100">
                {aiStatus === 'online' ? '🟢 Real AI Backend Online' : '🔴 Backend Disconnected'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2 relative z-10">
            <button
              onClick={() => setChatTheme(chatTheme === 'dark' ? 'crypto' : chatTheme === 'crypto' ? 'light' : 'dark')}
              className="p-1 hover:bg-white/20 rounded text-white transition-colors"
              title="Change Theme"
            >
              <Settings className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-1 hover:bg-white/20 rounded text-white transition-colors"
            >
              {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
            </button>
            <button
              onClick={onToggle}
              className="p-1 hover:bg-white/20 rounded text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 h-[calc(700px-180px)] custom-scrollbar">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start space-x-3 max-w-[90%] ${
                    message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                  }`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.type === 'user' 
                        ? 'bg-gradient-to-r from-blue-500 to-purple-500' 
                        : 'bg-gradient-to-r from-purple-500 via-blue-500 to-green-500 animate-pulse'
                    }`}>
                      {message.type === 'user' ? (
                        <User className="w-4 h-4 text-white" />
                      ) : (
                        <Brain className="w-4 h-4 text-white" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className={`rounded-lg p-3 relative group ${
                        message.type === 'user'
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                          : `${themeClasses.message} shadow-lg`
                      }`}>
                        <div className="whitespace-pre-wrap text-sm leading-relaxed">
                          {message.content}
                        </div>
                        
                        {message.type === 'bot' && (
                          <div className="absolute top-2 right-2 flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => copyMessage(message.content)}
                              className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors"
                              title="Copy message"
                            >
                              <Copy className="w-3 h-3" />
                            </button>
                          </div>
                        )}
                      </div>
                      
                      <div className={`text-xs text-slate-500 mt-1 ${
                        message.type === 'user' ? 'text-right' : 'text-left'
                      }`}>
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                      
                      {/* Alerts */}
                      {message.alerts && message.alerts.length > 0 && (
                        <div className="mt-3 space-y-2">
                          {message.alerts.map((alert, index) => (
                            <div key={index} className={`flex items-center space-x-2 p-2 rounded-lg ${
                              alert.type === 'bullish' ? 'bg-green-600/20 text-green-300' :
                              alert.type === 'bearish' ? 'bg-red-600/20 text-red-300' :
                              alert.type === 'warning' ? 'bg-yellow-600/20 text-yellow-300' :
                              'bg-blue-600/20 text-blue-300'
                            }`}>
                              <AlertTriangle className="w-4 h-4" />
                              <span className="text-xs">{alert.message}</span>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {/* Tools */}
                      {message.tools && message.tools.length > 0 && (
                        <div className="mt-3">
                          <p className="text-xs text-slate-400 mb-2">Quick tools:</p>
                          <div className="flex flex-wrap gap-2">
                            {message.tools.map((tool, index) => (
                              <button
                                key={index}
                                onClick={() => handleToolAction(tool)}
                                className="flex items-center space-x-1 px-3 py-1 bg-gradient-to-r from-purple-600/20 to-blue-600/20 hover:from-purple-600/40 hover:to-blue-600/40 rounded-full text-xs text-purple-300 transition-all duration-200 hover:scale-105"
                              >
                                {tool.icon === 'calculator' && <Calculator className="w-3 h-3" />}
                                {tool.icon === 'trending-up' && <TrendingUp className="w-3 h-3" />}
                                {tool.icon === 'target' && <Target className="w-3 h-3" />}
                                <span>{tool.name}</span>
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {/* Suggestions */}
                      {message.suggestions && message.suggestions.length > 0 && (
                        <div className="mt-3 space-y-2">
                          <p className="text-xs text-slate-400">Suggested actions:</p>
                          <div className="grid grid-cols-2 gap-2">
                            {message.suggestions.map((suggestion, index) => (
                              <button
                                key={index}
                                onClick={() => handleSuggestionClick(suggestion)}
                                className="text-xs px-3 py-2 bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 rounded-lg transition-all duration-200 hover:scale-105 hover:text-white border border-slate-600/50 hover:border-slate-500"
                              >
                                {suggestion}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 via-blue-500 to-green-500 flex items-center justify-center animate-pulse">
                      <Brain className="w-4 h-4 text-white" />
                    </div>
                    <div className={`${themeClasses.message} rounded-lg p-3 shadow-lg`}>
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                      <p className="text-xs text-slate-400 mt-1">
                        {aiStatus === 'online' ? 'Real AI is thinking...' : 'Attempting to connect...'}
                      </p>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-slate-700/50 bg-slate-800/30 backdrop-blur-sm">
              <div className="flex items-center space-x-3">
                <div className="relative flex-1">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={isListening ? "🎤 Listening..." : "Ask me anything about crypto..."}
                    className={`w-full ${themeClasses.input} rounded-lg px-4 py-3 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all duration-200 pr-12`}
                    disabled={isTyping || isListening}
                  />
                  <button
                    onClick={toggleVoiceInput}
                    className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-1 rounded-full transition-colors ${
                      isListening ? 'text-red-400 animate-pulse' : 'text-slate-400 hover:text-white'
                    }`}
                    title="Voice Input"
                  >
                    {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                  </button>
                </div>
                <button
                  onClick={() => handleSendMessage()}
                  disabled={!inputMessage.trim() || isTyping || isListening}
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white p-3 rounded-lg transition-all duration-200 hover:scale-105 disabled:hover:scale-100"
                  title="Send Message"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
              
              {/* Status Bar */}
              <div className="flex items-center justify-between mt-3">
                <div className="flex items-center space-x-4">
                  <p className="text-xs text-slate-500 flex items-center">
                    <Brain className="w-3 h-3 mr-1" />
                    {aiStatus === 'online' ? 'Real AI • Live data' : 'Backend Error • Check connection'}
                  </p>
                  <div className="flex items-center space-x-1">
                    <div className={`w-2 h-2 rounded-full animate-pulse ${
                      aiStatus === 'online' ? 'bg-green-400' : 'bg-red-400'
                    }`}></div>
                    <span className={`text-xs ${
                      aiStatus === 'online' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {aiStatus === 'online' ? 'AI Online' : 'Offline'}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center justify-center mt-2">
                <p className="text-xs text-slate-500 flex items-center">
                  <HelpCircle className="w-3 h-3 mr-1" />
                  Powered by real AI • Not financial advice
                </p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
