import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuthStore } from '../store/authStore';
import OTPInput from '../components/Auth/OTPInput';

/**
 * Auth Page Component
 * Handles user login, registration, and OTP verification
 */
const Auth: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [showOtpInput, setShowOtpInput] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    otp: ''
  });
  const [sendingOtp, setSendingOtp] = useState(false);

  const { 
    login, 
    register, 
    verifyOtp, 
    resendOtp, 
    isLoading, 
    isAuthenticated, 
    pendingOtpEmail,
    logout 
  } = useAuthStore();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Check if user wants to force auth (logout first)
  const forceAuth = searchParams.get('force') === 'true';

  // Check for pending OTP
  useEffect(() => {
    if (pendingOtpEmail) {
      setShowOtpInput(true);
    } else {
      setShowOtpInput(false);
    }
  }, [pendingOtpEmail]);

  // Redirect if already authenticated, unless force=true
  useEffect(() => {
    if (isAuthenticated && !forceAuth) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate, forceAuth]);

  // Handle logout for switching accounts
  const handleSwitchAccount = () => {
    logout();
    setShowOtpInput(false);
    toast.success('Logged out successfully');
  };

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
        console.log('Attempting login...');
        const result = await login(formData.email, formData.password);
        
        // Check if OTP is required
        if (result.requiresOtp) {
          setShowOtpInput(true);
          toast.success('Please check your email for the verification code');
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

  const handleOtpVerify = async (otp: string) => {
    try {
      await verifyOtp(otp);
      toast.success('Successfully logged in!');
      
      setTimeout(() => {
        navigate('/dashboard', { replace: true });
      }, 100);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'OTP verification failed';
      toast.error(errorMessage);
      throw error; // Re-throw to let OTPInput handle UI state
    }
  };

  const handleOtpResend = async () => {
    try {
      setIsResending(true);
      await resendOtp();
      toast.success('Verification code sent to your email');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to resend code';
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsResending(false);
    }
  };

  const handleBackToLogin = () => {
    setShowOtpInput(false);
    logout(); // Clear pending OTP state
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSendCode = async () => {
    if (!formData.email) {
      toast.error('Enter your email first');
      return;
    }
    try {
      setSendingOtp(true);
      // Try preferred endpoint first: resend-otp
      const resp = await fetch('http://localhost:8000/api/auth/resend-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: formData.email }),
      });

      if (resp.ok) {
        useAuthStore.setState({ pendingOtpEmail: formData.email });
        toast.success('Verification code sent');
      } else if (resp.status === 404) {
        // Fallbacks for backends that don't expose /resend-otp
        if (isLogin) {
          // Require password to trigger login which sends OTP
          if (!formData.password) {
            throw new Error('Enter your password to request a login code');
          }
          const loginResp = await fetch('http://localhost:8000/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: formData.email, password: formData.password })
          });
          if (!loginResp.ok) {
            const data = await loginResp.json().catch(() => ({} as any));
            throw new Error((data as any).detail || 'Failed to initiate login OTP');
          }
          useAuthStore.setState({ pendingOtpEmail: formData.email });
          toast.success('Login code sent');
        } else {
          // Sign up flow: call register/start to send OTP
          if (!formData.password) {
            throw new Error('Set a strong password to request a sign-up code');
          }
          const regResp = await fetch('http://localhost:8000/api/auth/register/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: formData.name || 'User', email: formData.email, password: formData.password })
          });
          if (!regResp.ok) {
            const data = await regResp.json().catch(() => ({} as any));
            throw new Error((data as any).detail || 'Failed to initiate sign-up OTP');
          }
          useAuthStore.setState({ pendingOtpEmail: formData.email });
          toast.success('Sign-up code sent');
        }
      } else {
        const data = await resp.json().catch(() => ({} as any));
        throw new Error((data as any).detail || 'Failed to send OTP');
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to send code';
      toast.error(msg);
    } finally {
      setSendingOtp(false);
    }
  };

  const handleInlineVerify = async () => {
    if (!formData.otp) {
      toast.error('Enter the 6-digit code');
      return;
    }
    try {
      await verifyOtp(formData.otp);
      toast.success('Verified! Redirecting...');
      setTimeout(() => navigate('/dashboard', { replace: true }), 100);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Invalid code';
      toast.error(msg);
    }
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

          {/* Show OTP Input if OTP verification is pending */}
          {showOtpInput && pendingOtpEmail && (
            <div>
              <OTPInput
                onVerify={handleOtpVerify}
                onResend={handleOtpResend}
                email={pendingOtpEmail}
                isLoading={isLoading}
                isResending={isResending}
              />
              
              {/* Back to Login Button */}
              <div className="mt-6 text-center">
                <button
                  onClick={handleBackToLogin}
                  className="text-slate-400 hover:text-white text-sm transition-colors"
                >
                  ← Back to Login
                </button>
              </div>
            </div>
          )}

          {/* Show form only if not authenticated, not in force mode, and not showing OTP */}
          {(!isAuthenticated || !forceAuth) && !showOtpInput && (
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

            {/* Inline OTP section for both Login and Sign Up */}
            <div className="grid grid-cols-12 gap-2 items-end">
              <div className="col-span-7">
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  One-Time Code
                </label>
                <input
                  type="text"
                  name="otp"
                  value={formData.otp}
                  onChange={handleChange}
                  className="input-field w-full"
                  placeholder="Enter 6-digit code"
                  maxLength={6}
                  inputMode="numeric"
                />
              </div>
              <div className="col-span-5 flex gap-2">
                <button
                  type="button"
                  onClick={handleSendCode}
                  disabled={sendingOtp || !formData.email}
                  className="px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-white disabled:opacity-50"
                >
                  {sendingOtp ? 'Sending…' : 'Send Code'}
                </button>
                <button
                  type="button"
                  onClick={handleInlineVerify}
                  disabled={isLoading || formData.otp.length !== 6}
                  className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm text-white disabled:opacity-50"
                >
                  Verify
                </button>
              </div>
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
