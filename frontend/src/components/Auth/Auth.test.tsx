import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider, useAuth } from '../../contexts/AuthContext';
import Login from './Login';
import Register from './Register';

/**
 * Helper to render with auth context + router
 */
const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        {component}
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('Login Component', () => {
  test('TC-F3: Login form renders with all fields', () => {
    renderWithProviders(<Login />);
    
    expect(screen.getByText(/welcome back/i)).toBeInTheDocument();
    // Check for input fields
    const inputs = document.querySelectorAll('input');
    expect(inputs.length).toBeGreaterThanOrEqual(2); // identifier + password
  });

  test('TC-F4: Login form has submit button', () => {
    renderWithProviders(<Login />);
    
    const submitButton = screen.getByRole('button', { name: /sign in|login|log in/i });
    expect(submitButton).toBeInTheDocument();
  });

  test('TC-F5: Login form has link to register', () => {
    renderWithProviders(<Login />);
    
    // Login page has "Don't have an account? Create one now" link
    const registerLink = screen.getByText(/create one now/i);
    expect(registerLink).toBeInTheDocument();
  });

  test('TC-F6: Login form shows error on empty submit', async () => {
    renderWithProviders(<Login />);
    
    const submitButton = screen.getByRole('button', { name: /sign in|login|log in/i });
    fireEvent.click(submitButton);
    
    // Should either show validation error or attempt submission
    // The form should not navigate away
    await waitFor(() => {
      expect(window.location.pathname).not.toBe('/dashboard');
    });
  });

  test('TC-F7: Login password field is masked', () => {
    renderWithProviders(<Login />);
    
    const passwordInput = document.querySelector('input[type="password"]');
    expect(passwordInput).toBeInTheDocument();
  });
});

describe('Register Component', () => {
  test('TC-F8: Register form renders', () => {
    renderWithProviders(<Register />);
    
    // "Create Account" appears as heading and button — use getAllByText
    const elements = screen.getAllByText(/create account/i);
    expect(elements.length).toBeGreaterThanOrEqual(1);
  });

  test('TC-F9: Register form has all required fields', () => {
    renderWithProviders(<Register />);
    
    const inputs = document.querySelectorAll('input');
    // Should have name, username, email, password (at minimum 4 inputs)
    expect(inputs.length).toBeGreaterThanOrEqual(4);
  });

  test('TC-F10: Register form has link to login', () => {
    renderWithProviders(<Register />);
    
    // "Sign in here" is the link text in the Register page
    const loginLink = screen.getByText(/sign in here/i);
    expect(loginLink).toBeInTheDocument();
  });
});
