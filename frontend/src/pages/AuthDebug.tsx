import React from 'react';
import { useAuthStore } from '../store/authStore';

const AuthDebug: React.FC = () => {
  const authState = useAuthStore();
  const storedToken = localStorage.getItem('token');

  const handleTestLogin = async () => {
    try {
      await authState.login('test@example.com', 'password');
      console.log('Test login completed');
    } catch (error) {
      console.error('Test login failed:', error);
    }
  };

  const handleClearAuth = () => {
    authState.logout();
    localStorage.clear();
  };

  return (
    <div className="p-6 bg-slate-800 text-white min-h-screen">
      <h1 className="text-2xl mb-6">Auth Debug Panel</h1>
      
      <div className="mb-6">
        <h2 className="text-xl mb-3">Current Auth State:</h2>
        <pre className="bg-slate-900 p-4 rounded">
          {JSON.stringify({
            isAuthenticated: authState.isAuthenticated,
            user: authState.user,
            token: authState.token,
            isLoading: authState.isLoading,
            storedToken: storedToken
          }, null, 2)}
        </pre>
      </div>

      <div className="space-x-4">
        <button 
          onClick={handleTestLogin}
          className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-700"
        >
          Test Login (test@example.com)
        </button>
        
        <button 
          onClick={handleClearAuth}
          className="bg-red-600 px-4 py-2 rounded hover:bg-red-700"
        >
          Clear Auth
        </button>
      </div>
    </div>
  );
};

export default AuthDebug;
