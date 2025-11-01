import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface User {
  id: string;
  email: string;
  name?: string;
  avatar?: string;
  createdAt: string;
  otpEnabled?: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  pendingOtpEmail: string | null;
  isRegistrationFlow: boolean; // Track if we're in registration or login flow
  login: (email: string, password: string) => Promise<{ requiresOtp?: boolean; email?: string }>;
  register: (name: string, email: string, password: string) => Promise<void>;
  verifyOtp: (otp: string, email?: string) => Promise<void>;
  resendOtp: () => Promise<void>;
  requestOtp: (email: string) => Promise<void>;
  enableOtp: (email: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      pendingOtpEmail: null,
      isRegistrationFlow: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        console.log('Login attempt for:', email);
        
        try {
          // Try backend first
          const response = await fetch('http://localhost:8000/api/auth/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
          });

          const data = await response.json();
          
          if (response.ok) {
            // Check if OTP is required
            if (data.requiresOtp) {
              set({ 
                pendingOtpEmail: email,
                isLoading: false,
                isRegistrationFlow: false // This is login flow
              });
              return { requiresOtp: true, email };
            }
            
            // Normal login success (shouldn't happen with our OTP-required setup)
            const { user, token } = data;
            set({
              user,
              token,
              isAuthenticated: true,
              isLoading: false,
              pendingOtpEmail: null
            });

            localStorage.setItem('token', token);
            console.log('Backend login successful for:', user.email);
            return {};
          } else {
            set({ isLoading: false });
            const errorMessage = data.detail || data.message || 'Login failed';
            throw new Error(errorMessage);
          }
        } catch (error) {
          set({ isLoading: false });
          if (error instanceof Error) {
            throw error;
          }
          throw new Error('Login failed - backend not available');
        }
      },

      register: async (name: string, email: string, password: string) => {
        set({ isLoading: true });
        try {
          // Always use backend for registration (sends OTP)
          const response = await fetch('http://localhost:8000/api/auth/register/start', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password }),
          });

          const data = await response.json();
          
          if (response.ok) {
            if (data.requires_otp || data.requiresOtp) {
              set({ 
                pendingOtpEmail: email, 
                isLoading: false,
                isRegistrationFlow: true // This is registration flow
              });
              console.log('✅ Registration OTP sent, awaiting verification');
              return;
            } else {
              set({ isLoading: false });
              throw new Error('Registration should require OTP verification');
            }
          } else {
            set({ isLoading: false });
            const errorMessage = data.detail || data.message || 'Registration failed';
            throw new Error(errorMessage);
          }
        } catch (error) {
          set({ isLoading: false });
          if (error instanceof Error) {
            throw error;
          }
          throw new Error('Registration failed - backend not available');
        }
      },

      verifyOtp: async (otp: string, email?: string) => {
        const { pendingOtpEmail, isRegistrationFlow } = get();
        const targetEmail = email || pendingOtpEmail;
        if (!targetEmail) throw new Error('No OTP verification pending');

        set({ isLoading: true });
        
        try {
          console.log('🔍 Attempting OTP verification for:', targetEmail, 'with OTP:', otp);
          console.log('🔍 Registration flow:', isRegistrationFlow);
          
          // Use smart OTP verification that automatically detects the correct flow
          console.log('🤖 Using smart OTP verification...');
          
          const response = await fetch('http://localhost:8000/api/auth/verify-otp-smart', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: targetEmail, otp: otp }),
          });

          console.log('🔍 OTP verify response status:', response.status);

          if (response.ok) {
            const data = await response.json();
            console.log('🔍 Success response data:', data);
            const { user, token } = data;

            set({
              user,
              token,
              isAuthenticated: true,
              isLoading: false,
              pendingOtpEmail: null,
              isRegistrationFlow: false
            });

            localStorage.setItem('token', token);
            console.log('✅ OTP verification successful');
          } else {
            set({ isLoading: false });
            try {
              const errorData = await response.json();
              console.error('🔍 Error response:', errorData);
              const errorMessage = errorData.detail || errorData.message || `Request failed with status ${response.status}`;
              throw new Error(errorMessage);
            } catch (jsonError) {
              console.error('🔍 Failed to parse error response:', jsonError);
              throw new Error(`Request failed with status ${response.status}`);
            }
          }
        } catch (error) {
          set({ isLoading: false });
          console.error('🔍 OTP verification error:', error);
          
          if (error instanceof Error) {
            throw error;
          } else if (typeof error === 'string') {
            throw new Error(error);
          } else {
            const errorMessage = (error as any)?.message || (error as any)?.detail || 'OTP verification failed';
            throw new Error(errorMessage);
          }
        }
      },

      requestOtp: async (email: string) => {
        if (!email) throw new Error('Email is required');
        try {
          const response = await fetch('http://localhost:8000/api/auth/resend-otp', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to send OTP');
          }

          // Set pending email so verifyOtp works without explicit email
          set({ pendingOtpEmail: email });
        } catch (error) {
          throw error;
        }
      },

      resendOtp: async () => {
        const { pendingOtpEmail } = get();
        if (!pendingOtpEmail) throw new Error('No OTP verification pending');

        try {
          const response = await fetch('http://localhost:8000/api/auth/resend-otp', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: pendingOtpEmail }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to resend OTP');
          }

          console.log('OTP resent successfully');
        } catch (error) {
          throw error;
        }
      },

      enableOtp: async (email: string) => {
        try {
          const response = await fetch('http://localhost:8000/api/auth/enable-otp', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to enable OTP');
          }

          // Update user state to reflect OTP is enabled
          const { user } = get();
          if (user) {
            set({
              user: { ...user, otpEnabled: true }
            });
          }

          console.log('OTP enabled successfully');
        } catch (error) {
          throw error;
        }
  },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          pendingOtpEmail: null
        });
        localStorage.removeItem('token');
      },

      setUser: (user: User) => {
        set({ user });
      },

      setToken: (token: string) => {
        set({ token, isAuthenticated: true });
        localStorage.setItem('token', token);
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        console.log('Auth store rehydrated:', state);
        if (!state) return;
        
        // Check if we have a token but lost authentication state
        if (state.token && !state.isAuthenticated) {
          console.log('Found token but not authenticated, fixing state');
          state.isAuthenticated = true;
        }
        // Also check localStorage directly as backup
        const storedToken = localStorage.getItem('token');
        if (storedToken && !state.token) {
          console.log('Found token in localStorage but not in state, updating');
          state.token = storedToken;
          state.isAuthenticated = true;
        }
      },
    }
  )
);
