import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

// Styles
import './styles/TradingView.css';

// Error Boundary
import ErrorBoundary from './components/ErrorBoundary';

// Authentication Context
import { AuthProvider } from './contexts/AuthContext';

// Pages
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import Portfolio from './pages/Portfolio';
// import Auth from './pages/Auth'; // Removed - using Login/Register components instead
import Settings from './pages/Settings';
import Profile from './pages/Profile';
import AuthDebug from './pages/AuthDebug';
import CryptoAnalysis from './pages/CryptoAnalysis';
import AlertsPage from './pages/AlertsPage';
import TradingSignalsPage from './pages/TradingSignalsPage';
import NewsPage from './pages/NewsPage';

// Authentication Components
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';

// Components
import Layout from './components/Layout/Layout';
import ProtectedRoute from './components/Auth/ProtectedRoute';

// Store
// import { useAuthStore } from './store/authStore'; // Currently unused

// Styles
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <Router>
        <div className="App min-h-screen bg-slate-900">
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1e293b',
                color: '#f8fafc',
                border: '1px solid #475569',
              },
            }}
          />
          
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            {/* Redirect /auth to /login for clean authentication */}
            <Route path="/auth" element={<Login />} />
            <Route path="/debug" element={<AuthDebug />} />
            
            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Analytics />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/portfolio"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Portfolio />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Settings />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />
            
            {/* Crypto Analysis Routes */}
            <Route
              path="/crypto/:symbol"
              element={
                <ProtectedRoute>
                  <Layout>
                    <CryptoAnalysis />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            {/* New AI Feature Routes */}
            <Route
              path="/alerts"
              element={
                <ProtectedRoute>
                  <Layout>
                    <AlertsPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/trading-signals"
              element={
                <ProtectedRoute>
                  <Layout>
                    <TradingSignalsPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/news"
              element={
                <ProtectedRoute>
                  <Layout>
                    <NewsPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            
            {/* Technical Analysis Routes */}

          </Routes>
        </div>
          </Router>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
