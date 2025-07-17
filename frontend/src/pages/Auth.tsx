import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuthStore } from '../store/authStore';

/**
 * Auth Page Component
 * Handles user login and registration
 */
const Auth: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  });

  const { login, register, isLoading, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Check if user wants to force auth (logout first)
  const forceAuth = searchParams.get('force') === 'true';

  // Redirect if already authenticated, unless force=true
  useEffect(() => {
    if (isAuthenticated && !forceAuth) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate, forceAuth]);

  // Handle logout for switching accounts
  const handleSwitchAccount = () => {
    logout();
    toast.success('Logged out successfully');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('Auth form submitted:', { email: formData.email, isLogin });
    
    try {
      if (isLogin) {
        console.log('Attempting login...');
        await login(formData.email, formData.password);
        console.log('Login completed, checking auth state...');
        toast.success('Successfully logged in!');
      } else {
        console.log('Attempting registration...');
        await register(formData.name, formData.email, formData.password);
        console.log('Registration completed, checking auth state...');
        toast.success('Account created successfully!');
      }
      
      // Wait a moment for state to update
      setTimeout(() => {
        console.log('Navigating to dashboard...');
        navigate('/dashboard', { replace: true });
      }, 100);
      
    } catch (error) {
      console.error('Auth error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Authentication failed';
      toast.error(isLogin ? `Login failed: ${errorMessage}` : `Registration failed: ${errorMessage}`);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="glass rounded-2xl p-8 shadow-2xl">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold gradient-text mb-2">
              Crypto Analytics
            </h1>
            <p className="text-slate-400">
              {isLogin ? 'Welcome back!' : 'Create your account'}
            </p>
          </div>

          {/* Show this if user is already authenticated and force=true */}
          {isAuthenticated && forceAuth && (
            <div className="mb-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
              <p className="text-blue-400 text-sm mb-3">
                You're already logged in. Would you like to:
              </p>
              <div className="space-y-2">
                <button
                  onClick={() => navigate('/dashboard')}
                  className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  Go to Dashboard
                </button>
                <button
                  onClick={handleSwitchAccount}
                  className="w-full px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded-lg transition-colors"
                >
                  Switch Account
                </button>
              </div>
            </div>
          )}

          {/* Show form only if not authenticated or if user isn't in force mode */}
          {(!isAuthenticated || !forceAuth) && (
            <>
            <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="input-field w-full"
                  placeholder="Enter your full name"
                  required
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Email Address
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="input-field w-full"
                placeholder="Enter your email"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="input-field w-full"
                placeholder="Enter your password"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full mt-6 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Loading...' : (isLogin ? 'Sign In' : 'Create Account')}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-slate-400">
              {isLogin ? "Don't have an account? " : "Already have an account? "}
              <button
                onClick={() => setIsLogin(!isLogin)}
                className="text-blue-400 hover:text-blue-300 font-medium"
              >
                {isLogin ? 'Sign up' : 'Sign in'}
              </button>
            </p>
          </div>
          </>
          )}

          <div className="mt-8 pt-6 border-t border-slate-600">
            <p className="text-xs text-slate-500 text-center">
              By continuing, you agree to our Terms of Service and Privacy Policy
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Auth;
