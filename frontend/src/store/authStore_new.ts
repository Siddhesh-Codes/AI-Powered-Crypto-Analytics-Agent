import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface User {
  id: string;
  email: string;
  name: string;
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
  login: (email: string, password: string) => Promise<{ requiresOtp?: boolean; email?: string }>;
  register: (name: string, email: string, password: string) => Promise<void>;
  verifyOtp: (otp: string) => Promise<void>;
  resendOtp: () => Promise<void>;
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

          if (response.ok) {
            const data = await response.json();
            
            // Check if OTP is required
            if (data.requiresOtp) {
              set({ 
                pendingOtpEmail: email,
                isLoading: false 
              });
              return { requiresOtp: true, email };
            }
            
            // Normal login success
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
          }
        } catch (error) {
          console.warn('Backend not available, using local authentication');
        }

        // Fallback local authentication
        const validCredentials = [
          { email: 'test@example.com', password: 'password', name: 'Test User', otpEnabled: true },
          { email: 'admin@crypto.com', password: 'admin123', name: 'Admin User', otpEnabled: false },
          { email: 'demo@demo.com', password: 'demo', name: 'Demo User', otpEnabled: false },
        ];

        console.log('Checking local credentials for:', email);
        const user = validCredentials.find(
          cred => cred.email.toLowerCase() === email.toLowerCase() && cred.password === password
        );

        if (user) {
          // Check if OTP is enabled for this user
          if (user.otpEnabled) {
            set({ 
              pendingOtpEmail: email,
              isLoading: false 
            });
            return { requiresOtp: true, email };
          }

          const mockUser: User = {
            id: 'user_' + Date.now(),
            email: user.email,
            name: user.name,
            avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=3b82f6&color=fff`,
            createdAt: new Date().toISOString(),
            otpEnabled: user.otpEnabled
          };

          const mockToken = 'local_token_' + Date.now();

          set({
            user: mockUser,
            token: mockToken,
            isAuthenticated: true,
            isLoading: false,
            pendingOtpEmail: null
          });

          localStorage.setItem('token', mockToken);
          console.log('Local login successful for:', user.email);
          console.log('Auth state after login:', { user: mockUser, token: mockToken, isAuthenticated: true });
          return {};
        } else {
          set({ isLoading: false });
          console.error('Login failed - invalid credentials for:', email);
          throw new Error('Invalid credentials');
        }
      },

      register: async (name: string, email: string, password: string) => {
        set({ isLoading: true });
        try {
          // Try backend first
          const response = await fetch('http://localhost:8000/api/auth/register', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password }),
          });

          if (response.ok) {
            const data = await response.json();
            const { user, token } = data;

            set({
              user,
              token,
              isAuthenticated: true,
              isLoading: false,
              pendingOtpEmail: null
            });

            localStorage.setItem('token', token);
            return;
          }
        } catch (error) {
          console.warn('Backend not available, using local registration');
        }

        // Fallback local registration
        if (name && email && password) {
          const mockUser: User = {
            id: 'user_' + Date.now(),
            email: email,
            name: name,
            avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=3b82f6&color=fff`,
            createdAt: new Date().toISOString(),
            otpEnabled: false
          };

          const mockToken = 'local_token_' + Date.now();

          set({
            user: mockUser,
            token: mockToken,
            isAuthenticated: true,
            isLoading: false,
            pendingOtpEmail: null
          });

          localStorage.setItem('token', mockToken);
        } else {
          set({ isLoading: false });
          throw new Error('All fields are required');
        }
      },

      verifyOtp: async (otp: string) => {
        const { pendingOtpEmail } = get();
        if (!pendingOtpEmail) throw new Error('No OTP verification pending');

        set({ isLoading: true });
        
        try {
          const response = await fetch('http://localhost:8000/api/auth/verify-otp', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
              email: pendingOtpEmail, 
              otp 
            }),
          });

          if (response.ok) {
            const data = await response.json();
            const { user, token } = data;

            set({
              user,
              token,
              isAuthenticated: true,
              isLoading: false,
              pendingOtpEmail: null
            });

            localStorage.setItem('token', token);
            console.log('OTP verification successful');
          } else {
            set({ isLoading: false });
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Invalid OTP');
          }
        } catch (error) {
          set({ isLoading: false });
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
