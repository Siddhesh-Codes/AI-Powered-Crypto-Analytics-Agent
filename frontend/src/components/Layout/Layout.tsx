import React, { ReactNode, useState } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import { AIChatbot } from '../AI/AIChatbot';

interface LayoutProps {
  children: ReactNode;
}

/**
 * Main Layout Component
 * Provides the overall structure with sidebar navigation and header
 */
const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);

  const toggleChatbot = () => {
    setIsChatbotOpen(!isChatbotOpen);
  };

  return (
    <div className="flex min-h-screen bg-slate-900">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <Header />
        
        {/* Page Content */}
        <main className="flex-1 bg-slate-900 min-h-0">
          {children}
        </main>
      </div>

      {/* AI Chatbot */}
      <AIChatbot 
        isOpen={isChatbotOpen} 
        onToggle={toggleChatbot}
      />
    </div>
  );
};

export default Layout;
