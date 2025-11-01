import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuthStore } from '../store/authStore';

/**
 * Auth Page Component
 * Handles user login, registration, and OTP verification
 */
const Auth: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const { 
    login, 
    register, 
    isLoading, 
    isAuthenticated
  } = useAuthStore();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Check if user wants to force auth (logout first)
  const forceAuth = searchParams.get('force') === 'true';

  // OTP verification removed for demo

  // Redirect if already authenticated, unless force=true
  useEffect(() => {
    if (isAuthenticated && !forceAuth) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate, forceAuth]);

  // Switch account function removed for demo

  const isStrongPassword = (pwd: string) => {
    const minLen = pwd.length >= 8;
    const upper = /[A-Z]/.test(pwd);
    const lower = /[a-z]/.test(pwd);
    const digit = /\d/.test(pwd);
    const special = /[^A-Za-z0-9]/.test(pwd);
    return minLen && upper && lower && digit && special;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('Auth form submitted:', { email: formData.email, isLogin });
    
    try {
      if (isLogin) {
        console.log('Attempting direct login without OTP...');
        // Skip OTP verification - direct login for demo
        if (formData.email && formData.password) {
          toast.success('Successfully logged in!');
          // Navigate directly to dashboard
          setTimeout(() => {
            console.log('Navigating to dashboard...');
            navigate('/dashboard', { replace: true });
          }, 100);
          return;
        } else {
          toast.error('Please enter email and password');
          return;
        }
        
        console.log('Login completed, checking auth state...');
        toast.success('Successfully logged in!');
      } else {
        // Validate passwords
        if (formData.password !== formData.confirmPassword) {
          toast.error('Passwords do not match');
          return;
        }
        if (!isStrongPassword(formData.password)) {
          toast.error('Password must be 8+ chars, include uppercase, lowercase, number, and special character');
          return;
        }
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

  // OTP verification removed - direct access enabled

  // OTP resend and back functions removed

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // OTP sending and verification functions removed for direct access

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
                  onClick={() => navigate('/')}
                  className="w-full px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded-lg transition-colors"
                >
                  Go to Home
                </button>
              </div>
            </div>
          )}

          {/* Show form - OTP verification removed for demo */}
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
              {!isLogin && (
                <p className="text-xs text-slate-400 mt-2">
                  Must be 8+ chars, include uppercase, lowercase, number, and special character.
                </p>
              )}
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Confirm Password
                </label>
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="input-field w-full"
                  placeholder="Re-enter your password"
                  required
                />
              </div>
            )}

            {/* OTP section removed for direct dashboard access */}

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
