import React from 'react';
import { renderHook, act } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthContext';

/**
 * Wrapper component for testing hooks
 */
const wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AuthProvider>{children}</AuthProvider>
);

describe('AuthContext', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.restoreAllMocks();
  });

  test('TC-F14: useAuth returns context values', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    expect(result.current).toHaveProperty('user');
    expect(result.current).toHaveProperty('isAuthenticated');
    expect(result.current).toHaveProperty('isLoading');
    expect(result.current).toHaveProperty('login');
    expect(result.current).toHaveProperty('register');
    expect(result.current).toHaveProperty('logout');
  });

  test('TC-F15: Initial state is unauthenticated', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    // Wait for loading to finish
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100));
    });
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });

  test('TC-F16: useAuth throws outside of AuthProvider', () => {
    // This should throw an error
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => {
      renderHook(() => useAuth());
    }).toThrow('useAuth must be used within an AuthProvider');
    
    consoleSpy.mockRestore();
  });

  test('TC-F17: Logout clears auth state', async () => {
    localStorage.setItem('auth_token', 'fake-token');
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    act(() => {
      result.current.logout();
    });
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(localStorage.getItem('auth_token')).toBeNull();
  });

  test('TC-F18: Login function exists and is callable', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    expect(typeof result.current.login).toBe('function');
  });

  test('TC-F19: Register function exists and is callable', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    expect(typeof result.current.register).toBe('function');
  });
});
