import React, { ReactNode, useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

interface ProtectedRouteProps {
  children: ReactNode;
}

/**
 * Protected Route Component
 * Redirects to auth page if user is not authenticated
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, user, token } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);

  // Wait for Zustand store rehydration
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 200); // Increased delay to ensure store rehydration

    return () => clearTimeout(timer);
  }, []);

  // Debug logging
  console.log('ProtectedRoute check:', { 
    isAuthenticated, 
    hasUser: !!user, 
    hasToken: !!token, 
    isLoading,
    userEmail: user?.email 
  });

  // Show loading during store rehydration
  if (isLoading) {
    console.log('ProtectedRoute: Still loading, showing loading screen');
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  // Simple check - if not authenticated, redirect
  if (!isAuthenticated) {
    console.log('Not authenticated, redirecting to /auth');
    return <Navigate to="/auth" replace />;
  }

  console.log('User authenticated, showing protected content');
  return <>{children}</>;
};

export default ProtectedRoute;
